from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, Http404
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.db.models import Sum
from django.utils.translation import gettext as _, ngettext
import json

from .models import (
    DebtAssets, StockAssets, MutualFundAssets, 
    GoldAssets, CryptoAssets, RealEstateAssets, Liabilities, Transactions, Documents
)
from .forms import (
    DebtAssetsForm, StockAssetsForm, MutualFundAssetsForm,
    GoldAssetsForm, CryptoAssetsForm, RealEstateAssetsForm, LiabilitiesForm, TransactionsForm,
    DocumentsForm
)
from .constants import (
    DEBT_ASSET_TYPE_CHOICES, STOCK_ASSET_TYPE_CHOICES, GOLD_ASSET_TYPE_CHOICES,
    DOCUMENT_ALLOWED_EXTENSIONS, DOCUMENT_MAX_FILE_SIZE, DOCUMENT_MAX_FILE_SIZE_MB
)


def item_count_label(count):
    """Localized, pluralized item count label"""
    return ngettext('item_count', 'item_count_plural', count) % {'counter': count}


@login_required(login_url='login_signup')
def portfolio_overview(request):
    """Main portfolio overview dashboard"""
    user = request.user
    
    # Fetch all asset totals
    debt_total = DebtAssets.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    stock_total = StockAssets.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    mutual_fund_total = MutualFundAssets.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    gold_total = GoldAssets.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    crypto_total = CryptoAssets.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    real_estate_total = RealEstateAssets.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    
    # Fetch liabilities
    liabilities_total = Liabilities.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate totals
    total_assets = debt_total + stock_total + mutual_fund_total + gold_total + crypto_total + real_estate_total
    net_worth = total_assets - liabilities_total
    
    # Get counts
    debt_count = DebtAssets.objects.filter(user=user).count()
    stock_count = StockAssets.objects.filter(user=user).count()
    mutual_fund_count = MutualFundAssets.objects.filter(user=user).count()
    gold_count = GoldAssets.objects.filter(user=user).count()
    crypto_count = CryptoAssets.objects.filter(user=user).count()
    real_estate_count = RealEstateAssets.objects.filter(user=user).count()
    liabilities_count = Liabilities.objects.filter(user=user).count()
    
    # Get recent items (last 5 of each)
    recent_assets = []
    
    for asset in DebtAssets.objects.filter(user=user).order_by('-created_at')[:5]:
        recent_assets.append({
            'name': asset.name,
            'type': _('recent_type_debt_asset'),
            'amount': asset.amount,
            'display_amount': asset.amount,
            'created_at': asset.created_at
        })
    
    for asset in StockAssets.objects.filter(user=user).order_by('-created_at')[:5]:
        recent_assets.append({
            'name': asset.name,
            'type': _('recent_type_stock_asset'),
            'amount': asset.amount,
            'display_amount': asset.amount,
            'created_at': asset.created_at
        })
    
    for asset in MutualFundAssets.objects.filter(user=user).order_by('-created_at')[:5]:
        recent_assets.append({
            'name': asset.name,
            'type': _('recent_type_mutual_fund'),
            'amount': asset.amount,
            'display_amount': asset.amount,
            'created_at': asset.created_at
        })
    
    for asset in GoldAssets.objects.filter(user=user).order_by('-created_at')[:5]:
        recent_assets.append({
            'name': asset.name,
            'type': _('recent_type_gold_asset'),
            'amount': asset.amount,
            'display_amount': asset.amount,
            'created_at': asset.created_at
        })
    
    for asset in CryptoAssets.objects.filter(user=user).order_by('-created_at')[:5]:
        recent_assets.append({
            'name': asset.name,
            'type': _('recent_type_crypto_asset'),
            'amount': asset.amount,
            'display_amount': asset.amount,
            'created_at': asset.created_at
        })
    
    for asset in RealEstateAssets.objects.filter(user=user).order_by('-created_at')[:5]:
        recent_assets.append({
            'name': asset.name,
            'type': _('recent_type_real_estate'),
            'amount': asset.amount,
            'display_amount': asset.amount,
            'created_at': asset.created_at
        })
    
    for liability in Liabilities.objects.filter(user=user).order_by('-created_at')[:5]:
        recent_assets.append({
            'name': liability.name,
            'type': _('recent_type_liability'),
            'amount': -liability.amount,  # Negative for liabilities
            'display_amount': liability.amount,  # Positive for display
            'created_at': liability.created_at
        })
    
    # Sort by date and take top 10
    recent_assets.sort(key=lambda x: x['created_at'], reverse=True)
    recent_assets = recent_assets[:10]
    
    context = {
        'total_assets': total_assets,
        'total_liabilities': liabilities_total,
        'net_worth': net_worth,
        'debt_total': debt_total,
        'stock_total': stock_total,
        'mutual_fund_total': mutual_fund_total,
        'gold_total': gold_total,
        'crypto_total': crypto_total,
        'real_estate_total': real_estate_total,
        'debt_count': debt_count,
        'stock_count': stock_count,
        'mutual_fund_count': mutual_fund_count,
        'gold_count': gold_count,
        'crypto_count': crypto_count,
        'real_estate_count': real_estate_count,
        'liabilities_count': liabilities_count,
        'debt_count_label': item_count_label(debt_count),
        'stock_count_label': item_count_label(stock_count),
        'mutual_fund_count_label': item_count_label(mutual_fund_count),
        'gold_count_label': item_count_label(gold_count),
        'crypto_count_label': item_count_label(crypto_count),
        'real_estate_count_label': item_count_label(real_estate_count),
        'liabilities_count_label': item_count_label(liabilities_count),
        'holdings_label': _('portfolio_across_holdings') % {
            'holdings': debt_count + stock_count + mutual_fund_count + gold_count + crypto_count + real_estate_count
        },
        'recent_assets': recent_assets,
    }
    
    return render(request, 'AssetsLiabilities/portfolio_overview.html', context)


# Generic CRUD Views Factory
class AssetViewFactory:
    """Factory to generate CRUD views for different asset types"""
    
    @staticmethod
    def create_views(model, form_class, template_name, asset_type, has_types=False, type_choices=None, extra_fields=None, show_total=True):
        """Generate all CRUD views for an asset type
        
        Args:
            extra_fields: List of additional field names to include in API responses (e.g., ['large_cap_percentage', 'mid_cap_percentage'])
            show_total: Whether the list response includes the sum of all amounts (off where adding them up has no meaning)
        """
        
        @login_required(login_url='login_signup')
        def list_view(request):
            """List all assets of this type for the user"""
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                field_list = ['id', 'name', 'amount', 'created_at']
                if has_types:
                    field_list.insert(2, 'type')
                if extra_fields:
                    field_list.extend(extra_fields)
                
                assets = model.objects.filter(user=request.user).values(*field_list)
                
                assets_list = []
                for asset in assets:
                    asset_dict = dict(asset)
                    if has_types:
                        asset_dict['type'] = dict(type_choices).get(asset['type'], asset['type'])
                    assets_list.append(asset_dict)
                
                response = {'assets': assets_list}
                if show_total:
                    response['total'] = model.objects.filter(user=request.user).aggregate(
                        total=Sum('amount')
                    )['total'] or 0
                return JsonResponse(response)
            
            context = {'asset_type': asset_type}
            if has_types:
                context['asset_types'] = type_choices
            return render(request, template_name, context)
        
        @login_required(login_url='login_signup')
        @require_http_methods(["POST"])
        def create_view(request):
            """Create a new asset"""
            try:
                data = json.loads(request.body)
                form = form_class(data)
                if form.is_valid():
                    asset = form.save(commit=False)
                    asset.user = request.user
                    asset.save()
                    return JsonResponse({'success': True, 'id': asset.id})
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
        
        @login_required(login_url='login_signup')
        @require_http_methods(["GET"])
        def detail_view(request, pk):
            """Get asset details"""
            asset = get_object_or_404(model, pk=pk, user=request.user)
            data = {'id': asset.id, 'name': asset.name, 'amount': asset.amount}
            if has_types:
                data['type'] = asset.type
            if extra_fields:
                for field in extra_fields:
                    data[field] = getattr(asset, field)
            return JsonResponse(data)
        
        @login_required(login_url='login_signup')
        @require_http_methods(["PUT"])
        def update_view(request, pk):
            """Update an asset"""
            try:
                asset = get_object_or_404(model, pk=pk, user=request.user)
                data = json.loads(request.body)
                form = form_class(data, instance=asset)
                if form.is_valid():
                    form.save()
                    return JsonResponse({'success': True})
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
        
        @login_required(login_url='login_signup')
        @require_http_methods(["DELETE"])
        def delete_view(request, pk):
            """Delete an asset"""
            try:
                asset = get_object_or_404(model, pk=pk, user=request.user)
                asset.delete()
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
        
        return {
            'list': list_view,
            'create': create_view,
            'detail': detail_view,
            'update': update_view,
            'delete': delete_view
        }


# Generate views for each asset type
debt_assets_views = AssetViewFactory.create_views(
    DebtAssets, DebtAssetsForm, 'AssetsLiabilities/debt_assets.html',
    'debt-assets', has_types=True, type_choices=DEBT_ASSET_TYPE_CHOICES
)

stock_assets_views = AssetViewFactory.create_views(
    StockAssets, StockAssetsForm, 'AssetsLiabilities/stock_assets.html',
    'stock-assets', has_types=True, type_choices=STOCK_ASSET_TYPE_CHOICES
)

mutual_fund_views = AssetViewFactory.create_views(
    MutualFundAssets, MutualFundAssetsForm, 'AssetsLiabilities/mutual_funds.html',
    'mutual-funds', has_types=False, 
    extra_fields=['large_cap_percentage', 'mid_cap_percentage', 'small_cap_percentage', 'debt_percentage']
)

gold_assets_views = AssetViewFactory.create_views(
    GoldAssets, GoldAssetsForm, 'AssetsLiabilities/gold_assets.html',
    'gold-assets', has_types=True, type_choices=GOLD_ASSET_TYPE_CHOICES
)

crypto_assets_views = AssetViewFactory.create_views(
    CryptoAssets, CryptoAssetsForm, 'AssetsLiabilities/crypto_assets.html',
    'crypto-assets', has_types=False
)

real_estate_views = AssetViewFactory.create_views(
    RealEstateAssets, RealEstateAssetsForm, 'AssetsLiabilities/real_estate.html',
    'real-estate', has_types=False
)

liabilities_views = AssetViewFactory.create_views(
    Liabilities, LiabilitiesForm, 'AssetsLiabilities/liabilities.html',
    'liabilities', has_types=False
)

transactions_views = AssetViewFactory.create_views(
    Transactions, TransactionsForm, 'AssetsLiabilities/transactions.html',
    'transactions', has_types=False,
    extra_fields=['from_party', 'to_party'],
    show_total=False
)


# Export view functions
debt_assets_list = debt_assets_views['list']
debt_assets_create = debt_assets_views['create']
debt_assets_detail = debt_assets_views['detail']
debt_assets_update = debt_assets_views['update']
debt_assets_delete = debt_assets_views['delete']

stock_assets_list = stock_assets_views['list']
stock_assets_create = stock_assets_views['create']
stock_assets_detail = stock_assets_views['detail']
stock_assets_update = stock_assets_views['update']
stock_assets_delete = stock_assets_views['delete']

mutual_fund_list = mutual_fund_views['list']
mutual_fund_create = mutual_fund_views['create']
mutual_fund_detail = mutual_fund_views['detail']
mutual_fund_update = mutual_fund_views['update']
mutual_fund_delete = mutual_fund_views['delete']

gold_assets_list = gold_assets_views['list']
gold_assets_create = gold_assets_views['create']
gold_assets_detail = gold_assets_views['detail']
gold_assets_update = gold_assets_views['update']
gold_assets_delete = gold_assets_views['delete']

crypto_assets_list = crypto_assets_views['list']
crypto_assets_create = crypto_assets_views['create']
crypto_assets_detail = crypto_assets_views['detail']
crypto_assets_update = crypto_assets_views['update']
crypto_assets_delete = crypto_assets_views['delete']

real_estate_list = real_estate_views['list']
real_estate_create = real_estate_views['create']
real_estate_detail = real_estate_views['detail']
real_estate_update = real_estate_views['update']
real_estate_delete = real_estate_views['delete']

liabilities_list = liabilities_views['list']
liabilities_create = liabilities_views['create']
liabilities_detail = liabilities_views['detail']
liabilities_update = liabilities_views['update']
liabilities_delete = liabilities_views['delete']

transactions_list = transactions_views['list']
transactions_create = transactions_views['create']
transactions_detail = transactions_views['detail']
transactions_update = transactions_views['update']
transactions_delete = transactions_views['delete']


# Documents Views (file uploads are multipart, so they are not part of the JSON asset factory)
def _serialize_document(document):
    """Convert a document into the JSON shape used by the documents page"""
    return {
        'id': document.id,
        'name': document.name,
        'file_name': document.original_filename,
        'file_extension': document.original_filename.rsplit('.', 1)[-1].lower(),
        'file_size': document.file_size,
        'created_at': document.created_at,
        'file_url': reverse('documents_file', args=[document.id]),
        'download_url': reverse('documents_file', args=[document.id]) + '?download=1',
    }


@login_required(login_url='login_signup')
def documents_list(request):
    """List all documents of the user"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        documents = Documents.objects.filter(user=request.user)
        return JsonResponse({
            'assets': [_serialize_document(document) for document in documents],
            'total': documents.count()
        })
    
    context = {
        'asset_type': 'documents',
        'max_file_size': DOCUMENT_MAX_FILE_SIZE,
        'accepted_extensions': ','.join(f'.{extension}' for extension in DOCUMENT_ALLOWED_EXTENSIONS),
        'file_help_text': _('form_help_document_file') % {
            'extensions': ', '.join(extension.upper() for extension in DOCUMENT_ALLOWED_EXTENSIONS),
            'size': DOCUMENT_MAX_FILE_SIZE_MB
        },
    }
    return render(request, 'AssetsLiabilities/documents.html', context)


@login_required(login_url='login_signup')
@require_http_methods(["POST"])
def documents_create(request):
    """Upload a new document"""
    try:
        form = DocumentsForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            document.save()
            return JsonResponse({'success': True, 'id': document.id})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='login_signup')
@require_http_methods(["GET"])
def documents_detail(request, pk):
    """Get document details"""
    document = get_object_or_404(Documents, pk=pk, user=request.user)
    return JsonResponse({'id': document.id, 'name': document.name, 'file_name': document.original_filename})


@login_required(login_url='login_signup')
@require_http_methods(["POST"])
def documents_update(request, pk):
    """Rename a document and optionally replace its file"""
    try:
        document = get_object_or_404(Documents, pk=pk, user=request.user)
        form = DocumentsForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    except Http404:
        raise
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='login_signup')
@require_http_methods(["DELETE"])
def documents_delete(request, pk):
    """Delete a document and its stored file"""
    try:
        document = get_object_or_404(Documents, pk=pk, user=request.user)
        document.delete()
        return JsonResponse({'success': True})
    except Http404:
        raise
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='login_signup')
@require_http_methods(["GET"])
def documents_file(request, pk):
    """Serve the stored file to its owner only (inline, or as a download with ?download=1)"""
    document = get_object_or_404(Documents, pk=pk, user=request.user)
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
