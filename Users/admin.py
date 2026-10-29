from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .forms import UserAdditionalDataForm
from .models import UserAdditionalData

admin.site.site_header = _('admin_site_header')
admin.site.site_title = _('admin_site_title')
admin.site.index_title = _('admin_index_title')


def full_mobile_number(profile):
    return f'{profile.country_code} {profile.mobile_number}'


@admin.register(UserAdditionalData)
class UserAdditionalDataAdmin(admin.ModelAdmin):
    form = UserAdditionalDataForm
    list_display = ('user', 'first_name', 'last_name', 'mobile', 'user_email', 'created_at')
    list_select_related = ('user',)
    list_filter = ('country_code', 'created_at')
    search_fields = ('user__username', 'user__email', 'first_name', 'last_name', 'mobile_number')
    autocomplete_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 25
    fieldsets = (
        (None, {'fields': ('user', ('first_name', 'last_name'), ('country_code', 'mobile_number'))}),
        (_('admin_fieldset_timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    @admin.display(description=_('admin_col_mobile'), ordering='mobile_number')
    def mobile(self, obj):
        return full_mobile_number(obj)
    
    @admin.display(description=_('admin_col_email'), ordering='user__email')
    def user_email(self, obj):
        return obj.user.email


class UserAdditionalDataInline(admin.StackedInline):
    model = UserAdditionalData
    form = UserAdditionalDataForm
    can_delete = False
    fields = (('first_name', 'last_name'), ('country_code', 'mobile_number'))
    extra = 0
    max_num = 1


admin.site.unregister(User)


@admin.register(User)
class FinanceUserAdmin(UserAdmin):
    """Django user admin with the profile (name, mobile) shown inline and in the list"""
    inlines = (UserAdditionalDataInline,)
    list_display = ('username', 'email', 'profile_name', 'profile_mobile', 'is_active', 'is_staff', 'date_joined', 'last_login')
    list_select_related = ('useradditionaldata',)
    list_filter = UserAdmin.list_filter + ('date_joined', 'last_login')
    search_fields = UserAdmin.search_fields + ('useradditionaldata__mobile_number',)
    ordering = ('-date_joined',)
    list_per_page = 25
    
    @admin.display(description=_('admin_col_name'), ordering='useradditionaldata__first_name')
    def profile_name(self, obj):
        profile = getattr(obj, 'useradditionaldata', None)
        return f'{profile.first_name} {profile.last_name}' if profile else '-'
    
    @admin.display(description=_('admin_col_mobile'))
    def profile_mobile(self, obj):
        profile = getattr(obj, 'useradditionaldata', None)
        return full_mobile_number(profile) if profile else '-'
