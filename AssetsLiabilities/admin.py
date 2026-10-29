from django import forms
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .constants import DOCUMENT_ALLOWED_EXTENSIONS
from .forms import (
    DebtAssetsForm, StockAssetsForm, MutualFundAssetsForm, GoldAssetsForm, CryptoAssetsForm,
    RealEstateAssetsForm, LiabilitiesForm, TransactionsForm, DocumentsForm
)
from .models import (
    DebtAssets, StockAssets, MutualFundAssets, GoldAssets, CryptoAssets,
    RealEstateAssets, Liabilities, Transactions, Documents
)


def format_inr(amount):
    """Format a number as Indian Rupees with Indian digit grouping, e.g. ₹1,25,000"""
    sign = '-' if amount < 0 else ''
    digits = str(abs(int(amount)))
    if len(digits) > 3:
        head, tail = digits[:-3], digits[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        digits = ','.join(groups + [tail])
    return f'{sign}₹{digits}'


def format_file_size(size):
    """Human readable file size"""
    if size >= 1024 * 1024:
        return f'{size / (1024 * 1024):.1f} MB'
    return f'{max(1, round(size / 1024))} KB'


# ===== Base Admin =====

class UserOwnedAdmin(admin.ModelAdmin):
    """Common admin setup for records owned by a user.

    Subclasses set `form` to the app's ModelForm so the admin applies the same validation
    as the pages; the admin adds the `user` field from the fieldsets automatically.
    """
    main_fields = ('user', 'name', 'amount')
    list_select_related = ('user',)
    list_filter = (('user', admin.RelatedOnlyFieldListFilter), 'created_at')
    search_fields = ('name', 'user__username', 'user__email')
    autocomplete_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 25
    
    def get_fieldsets(self, request, obj=None):
        return [
            (None, {'fields': self.main_fields}),
            (_('admin_fieldset_timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
        ]
    
    @admin.display(description=_('admin_col_amount'), ordering='amount')
    def formatted_amount(self, obj):
        return format_inr(obj.amount)


class TypedAssetAdmin(UserOwnedAdmin):
    """Assets that are grouped by a type choice (debt, stock, gold)"""
    main_fields = ('user', 'name', 'type', 'amount')
    list_display = ('name', 'type', 'formatted_amount', 'user', 'created_at', 'updated_at')
    list_filter = ('type', ('user', admin.RelatedOnlyFieldListFilter), 'created_at')
    ordering = ('type', '-amount')


class SimpleAssetAdmin(UserOwnedAdmin):
    """Records with only a name and an amount (crypto, real estate, liabilities)"""
    list_display = ('name', 'formatted_amount', 'user', 'created_at', 'updated_at')
    ordering = ('-amount',)


# ===== Assets & Liabilities =====

@admin.register(DebtAssets)
class DebtAssetsAdmin(TypedAssetAdmin):
    form = DebtAssetsForm


@admin.register(StockAssets)
class StockAssetsAdmin(TypedAssetAdmin):
    form = StockAssetsForm


@admin.register(GoldAssets)
class GoldAssetsAdmin(TypedAssetAdmin):
    form = GoldAssetsForm


@admin.register(MutualFundAssets)
class MutualFundAssetsAdmin(UserOwnedAdmin):
    form = MutualFundAssetsForm
    list_display = (
        'name', 'formatted_amount', 'large_cap_percentage', 'mid_cap_percentage',
        'small_cap_percentage', 'debt_percentage', 'user', 'created_at'
    )
    ordering = ('-amount',)
    
    def get_fieldsets(self, request, obj=None):
        return [
            (None, {'fields': ('user', 'name', 'amount')}),
            (_('form_label_asset_allocation'), {'fields': (
                ('large_cap_percentage', 'mid_cap_percentage'),
                ('small_cap_percentage', 'debt_percentage'),
            )}),
            (_('admin_fieldset_timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
        ]


@admin.register(CryptoAssets)
class CryptoAssetsAdmin(SimpleAssetAdmin):
    form = CryptoAssetsForm


@admin.register(RealEstateAssets)
class RealEstateAssetsAdmin(SimpleAssetAdmin):
    form = RealEstateAssetsForm


@admin.register(Liabilities)
class LiabilitiesAdmin(SimpleAssetAdmin):
    form = LiabilitiesForm


# ===== Tools =====

@admin.register(Transactions)
class TransactionsAdmin(UserOwnedAdmin):
    form = TransactionsForm
    main_fields = ('user', 'name', ('from_party', 'to_party'), 'amount')
    list_display = ('name', 'from_party', 'to_party', 'formatted_amount', 'user', 'created_at')
    search_fields = ('name', 'from_party', 'to_party', 'user__username', 'user__email')


class DocumentFileTypeFilter(admin.SimpleListFilter):
    title = _('admin_filter_file_type')
    parameter_name = 'file_type'
    
    def lookups(self, request, model_admin):
        return [(extension, extension.upper()) for extension in DOCUMENT_ALLOWED_EXTENSIONS]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(original_filename__iendswith=f'.{self.value()}')
        return queryset


class DocumentFileSizeFilter(admin.SimpleListFilter):
    title = _('admin_filter_file_size')
    parameter_name = 'file_size'
    
    def lookups(self, request, model_admin):
        return [
            ('small', _('admin_size_under_1mb')),
            ('medium', _('admin_size_1_to_3mb')),
            ('large', _('admin_size_over_3mb')),
        ]
    
    def queryset(self, request, queryset):
        one_mb = 1024 * 1024
        if self.value() == 'small':
            return queryset.filter(file_size__lt=one_mb)
        if self.value() == 'medium':
            return queryset.filter(file_size__gte=one_mb, file_size__lte=3 * one_mb)
        if self.value() == 'large':
            return queryset.filter(file_size__gt=3 * one_mb)
        return queryset


class DocumentsAdminForm(DocumentsForm):
    """Admin uploads follow the same type/size/content rules as the Document Vault page"""
    
    class Meta(DocumentsForm.Meta):
        fields = ['user', 'name', 'file']
        # Plain file input: the default widget links to /media/, which is intentionally not served
        widgets = {'file': forms.FileInput}


@admin.register(Documents)
class DocumentsAdmin(UserOwnedAdmin):
    form = DocumentsAdminForm
    main_fields = ('user', 'name', 'file', 'original_filename', 'readable_size', 'file_links')
    list_display = ('name', 'original_filename', 'file_type', 'readable_size', 'user', 'created_at', 'file_links')
    list_filter = (
        ('user', admin.RelatedOnlyFieldListFilter), DocumentFileTypeFilter,
        DocumentFileSizeFilter, 'created_at'
    )
    search_fields = ('name', 'original_filename', 'user__username', 'user__email')
    readonly_fields = ('original_filename', 'readable_size', 'file_links', 'created_at', 'updated_at')
    
    @admin.display(description=_('admin_col_file_type'))
    def file_type(self, obj):
        return obj.original_filename.rsplit('.', 1)[-1].upper() if '.' in obj.original_filename else '-'
    
    @admin.display(description=_('admin_col_file_size'), ordering='file_size')
    def readable_size(self, obj):
        return format_file_size(obj.file_size) if obj.file_size else '-'
    
    @admin.display(description=_('admin_col_file'))
    def file_links(self, obj):
        if not obj.pk:
            return '-'
        url = reverse(f'admin:{self.opts.app_label}_{self.opts.model_name}_file', args=[obj.pk])
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">{}</a> | <a href="{}?download=1">{}</a>',
            url, _('btn_view'), url, _('btn_download')
        )
    
    def get_urls(self):
        info = (self.opts.app_label, self.opts.model_name)
        return [
            path('<int:pk>/file/', self.admin_site.admin_view(self.serve_file), name='%s_%s_file' % info),
        ] + super().get_urls()
    
    def serve_file(self, request, pk):
        """Serve a stored document to admins with view permission"""
        document = get_object_or_404(Documents, pk=pk)
        if not self.has_view_permission(request, document):
            raise PermissionDenied
        try:
            stored_file = document.file.open('rb')
        except FileNotFoundError:
            raise Http404
        response = FileResponse(
            stored_file,
            as_attachment=request.GET.get('download') == '1',
            filename=document.original_filename
        )
        response['X-Content-Type-Options'] = 'nosniff'
        return response
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        old_file_name = getattr(form, '_old_file_name', None)
        if change and old_file_name and old_file_name != obj.file.name:
            obj.file.storage.delete(old_file_name)
