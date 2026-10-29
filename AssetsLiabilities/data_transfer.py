"""Export a user's assets, liabilities and transactions to JSON and import them back (documents excluded)"""
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext as _, gettext_lazy

from .constants import DATA_EXPORT_APP_ID, DATA_EXPORT_VERSION
from .forms import (
    DebtAssetsForm, StockAssetsForm, MutualFundAssetsForm, GoldAssetsForm,
    CryptoAssetsForm, RealEstateAssetsForm, LiabilitiesForm, TransactionsForm
)
from .models import (
    DebtAssets, StockAssets, MutualFundAssets, GoldAssets,
    CryptoAssets, RealEstateAssets, Liabilities, Transactions
)

# (JSON key, model, form used to validate imports, display label)
# The exported fields are the form fields, so export and import always stay in sync
DATA_SECTIONS = (
    ('debt_assets', DebtAssets, DebtAssetsForm, gettext_lazy('nav_debt_assets')),
    ('stock_assets', StockAssets, StockAssetsForm, gettext_lazy('nav_stock_assets')),
    ('mutual_funds', MutualFundAssets, MutualFundAssetsForm, gettext_lazy('nav_mutual_funds')),
    ('gold_assets', GoldAssets, GoldAssetsForm, gettext_lazy('nav_gold_assets')),
    ('crypto_assets', CryptoAssets, CryptoAssetsForm, gettext_lazy('nav_crypto_assets')),
    ('real_estate', RealEstateAssets, RealEstateAssetsForm, gettext_lazy('nav_real_estate')),
    ('liabilities', Liabilities, LiabilitiesForm, gettext_lazy('nav_liabilities')),
    ('transactions', Transactions, TransactionsForm, gettext_lazy('nav_transactions')),
)


def export_user_data(user):
    """Build the export payload for a user"""
    return {
        'app': DATA_EXPORT_APP_ID,
        'version': DATA_EXPORT_VERSION,
        'exported_at': timezone.now().isoformat(),
        'username': user.username,
        'data': {
            key: list(
                model.objects.filter(user=user).order_by('created_at', 'id').values(*form_class._meta.fields)
            )
            for key, model, form_class, label in DATA_SECTIONS
        },
    }


def import_user_data(user, payload, replace_existing=False):
    """Validate every record first and save them all in one transaction only if all are valid.

    Returns (created, errors): created is a list of {'section', 'count'} and errors a list of messages.
    Unknown sections (e.g. documents) are ignored.
    """
    data = payload['data']
    valid_forms = []
    errors = []
    
    for key, model, form_class, label in DATA_SECTIONS:
        items = data.get(key, [])
        if not isinstance(items, list):
            errors.append(_('import_error_section_not_list') % {'section': label})
            continue
        for index, item in enumerate(items, start=1):
            if not isinstance(item, dict):
                errors.append(_('import_error_item_not_object') % {'section': label, 'index': index})
                continue
            form = form_class(item)
            if form.is_valid():
                valid_forms.append((key, form))
                continue
            for field, messages in form.errors.items():
                for message in messages:
                    if field == '__all__':
                        errors.append(_('import_error_record') % {'section': label, 'index': index, 'message': message})
                    else:
                        errors.append(_('import_error_record_field') % {
                            'section': label, 'index': index, 'field': field, 'message': message
                        })
    
    if errors:
        return [], errors
    if not valid_forms:
        return [], [_('import_error_empty')]
    
    counts = {key: 0 for key, model, form_class, label in DATA_SECTIONS}
    with transaction.atomic():
        if replace_existing:
            for key, model, form_class, label in DATA_SECTIONS:
                model.objects.filter(user=user).delete()
        for key, form in valid_forms:
            record = form.save(commit=False)
            record.user = user
            record.save()
            counts[key] += 1
    
    created = [
        {'section': str(label), 'count': counts[key]}
        for key, model, form_class, label in DATA_SECTIONS if counts[key]
    ]
    return created, []
