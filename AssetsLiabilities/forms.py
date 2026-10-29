import json

from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext_lazy as _
from .constants import (
    DOCUMENT_ALLOWED_EXTENSIONS, DOCUMENT_FILE_SIGNATURES,
    DOCUMENT_MAX_FILE_SIZE, DOCUMENT_MAX_FILE_SIZE_MB,
    DATA_EXPORT_APP_ID, DATA_EXPORT_VERSION,
    DATA_IMPORT_MAX_FILE_SIZE, DATA_IMPORT_MAX_FILE_SIZE_MB
)
from .models import (
    DebtAssets,
    StockAssets,
    MutualFundAssets,
    GoldAssets,
    CryptoAssets,
    RealEstateAssets,
    Liabilities,
    Transactions,
    Documents
)


class DebtAssetsForm(forms.ModelForm):
    """Form for creating/editing debt assets"""
    
    class Meta:
        model = DebtAssets
        fields = ['name', 'type', 'amount']
        
    def clean_name(self):
        """Validate name field"""
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise ValidationError(_('debt_asset_name_required'))
        if len(name.strip()) < 3:
            raise ValidationError(_('debt_asset_name_min_length'))
        return name.strip()
    
    def clean_type(self):
        """Validate type field"""
        asset_type = self.cleaned_data.get('type')
        if not asset_type:
            raise ValidationError(_('debt_asset_type_required'))
        return asset_type
    
    def clean_amount(self):
        """Validate amount is positive"""
        amount = self.cleaned_data.get('amount')
        if amount is None:
            raise ValidationError(_('debt_asset_amount_required'))
        if amount <= 0:
            raise ValidationError(_('debt_asset_amount_positive'))
        return amount


class StockAssetsForm(forms.ModelForm):
    """Form for creating/editing stock assets"""
    
    class Meta:
        model = StockAssets
        fields = ['name', 'type', 'amount']
        
    def clean_name(self):
        """Validate name field"""
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise ValidationError(_('stock_asset_name_required'))
        if len(name.strip()) < 3:
            raise ValidationError(_('stock_asset_name_min_length'))
        return name.strip()
    
    def clean_type(self):
        """Validate type field"""
        asset_type = self.cleaned_data.get('type')
        if not asset_type:
            raise ValidationError(_('stock_asset_type_required'))
        return asset_type
    
    def clean_amount(self):
        """Validate amount is positive"""
        amount = self.cleaned_data.get('amount')
        if amount is None:
            raise ValidationError(_('stock_asset_amount_required'))
        if amount <= 0:
            raise ValidationError(_('stock_asset_amount_positive'))
        return amount


class MutualFundAssetsForm(forms.ModelForm):
    """Form for creating/editing mutual fund assets"""
    
    class Meta:
        model = MutualFundAssets
        fields = [
            'name', 'amount',
            'large_cap_percentage', 'mid_cap_percentage',
            'small_cap_percentage', 'debt_percentage'
        ]
        
    def clean_name(self):
        """Validate name field"""
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise ValidationError(_('mutual_fund_asset_name_required'))
        if len(name.strip()) < 3:
            raise ValidationError(_('mutual_fund_asset_name_min_length'))
        return name.strip()
    
    def clean_amount(self):
        """Validate amount is positive"""
        amount = self.cleaned_data.get('amount')
        if amount is None:
            raise ValidationError(_('mutual_fund_asset_amount_required'))
        if amount <= 0:
            raise ValidationError(_('mutual_fund_asset_amount_positive'))
        return amount
    
    def clean_large_cap_percentage(self):
        """Validate large cap percentage"""
        percentage = self.cleaned_data.get('large_cap_percentage')
        if percentage is None:
            raise ValidationError(_('mutual_fund_large_cap_percentage_required'))
        if percentage < 0 or percentage > 100:
            raise ValidationError(_('mutual_fund_percentage_range_error'))
        return percentage
    
    def clean_mid_cap_percentage(self):
        """Validate mid cap percentage"""
        percentage = self.cleaned_data.get('mid_cap_percentage')
        if percentage is None:
            raise ValidationError(_('mutual_fund_mid_cap_percentage_required'))
        if percentage < 0 or percentage > 100:
            raise ValidationError(_('mutual_fund_percentage_range_error'))
        return percentage
    
    def clean_small_cap_percentage(self):
        """Validate small cap percentage"""
        percentage = self.cleaned_data.get('small_cap_percentage')
        if percentage is None:
            raise ValidationError(_('mutual_fund_small_cap_percentage_required'))
        if percentage < 0 or percentage > 100:
            raise ValidationError(_('mutual_fund_percentage_range_error'))
        return percentage
    
    def clean_debt_percentage(self):
        """Validate debt percentage"""
        percentage = self.cleaned_data.get('debt_percentage')
        if percentage is None:
            raise ValidationError(_('mutual_fund_debt_percentage_required'))
        if percentage < 0 or percentage > 100:
            raise ValidationError(_('mutual_fund_percentage_range_error'))
        return percentage
    
    # The "percentages must sum to 100" rule lives in MutualFundAssets.clean(), which ModelForm
    # validation runs automatically and reports as a form-level (__all__) error


class GoldAssetsForm(forms.ModelForm):
    """Form for creating/editing gold assets"""
    
    class Meta:
        model = GoldAssets
        fields = ['name', 'type', 'amount']
        
    def clean_name(self):
        """Validate name field"""
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise ValidationError(_('gold_asset_name_required'))
        if len(name.strip()) < 3:
            raise ValidationError(_('gold_asset_name_min_length'))
        return name.strip()
    
    def clean_type(self):
        """Validate type field"""
        asset_type = self.cleaned_data.get('type')
        if not asset_type:
            raise ValidationError(_('gold_asset_type_required'))
        return asset_type
    
    def clean_amount(self):
        """Validate amount is positive"""
        amount = self.cleaned_data.get('amount')
        if amount is None:
            raise ValidationError(_('gold_asset_amount_required'))
        if amount <= 0:
            raise ValidationError(_('gold_asset_amount_positive'))
        return amount


class CryptoAssetsForm(forms.ModelForm):
    """Form for creating/editing cryptocurrency assets"""
    
    class Meta:
        model = CryptoAssets
        fields = ['name', 'amount']
        
    def clean_name(self):
        """Validate name field"""
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise ValidationError(_('crypto_asset_name_required'))
        if len(name.strip()) < 2:
            raise ValidationError(_('crypto_asset_name_min_length'))
        return name.strip()
    
    def clean_amount(self):
        """Validate amount is positive"""
        amount = self.cleaned_data.get('amount')
        if amount is None:
            raise ValidationError(_('crypto_asset_amount_required'))
        if amount <= 0:
            raise ValidationError(_('crypto_asset_amount_positive'))
        return amount


class RealEstateAssetsForm(forms.ModelForm):
    """Form for creating/editing real estate assets"""
    
    class Meta:
        model = RealEstateAssets
        fields = ['name', 'amount']
        
    def clean_name(self):
        """Validate name field"""
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise ValidationError(_('real_estate_asset_name_required'))
        if len(name.strip()) < 3:
            raise ValidationError(_('real_estate_asset_name_min_length'))
        return name.strip()
    
    def clean_amount(self):
        """Validate amount is positive"""
        amount = self.cleaned_data.get('amount')
        if amount is None:
            raise ValidationError(_('real_estate_asset_amount_required'))
        if amount <= 0:
            raise ValidationError(_('real_estate_asset_amount_positive'))
        return amount


class LiabilitiesForm(forms.ModelForm):
    """Form for creating/editing liabilities"""
    
    class Meta:
        model = Liabilities
        fields = ['name', 'amount']
        
    def clean_name(self):
        """Validate name field"""
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise ValidationError(_('liability_name_required'))
        if len(name.strip()) < 3:
            raise ValidationError(_('liability_name_min_length'))
        return name.strip()
    
    def clean_amount(self):
        """Validate amount is positive"""
        amount = self.cleaned_data.get('amount')
        if amount is None:
            raise ValidationError(_('liability_amount_required'))
        if amount <= 0:
            raise ValidationError(_('liability_amount_positive'))
        return amount


class TransactionsForm(forms.ModelForm):
    """Form for creating/editing transactions"""
    
    class Meta:
        model = Transactions
        fields = ['name', 'from_party', 'to_party', 'amount']
        
    def clean_name(self):
        """Validate name field"""
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise ValidationError(_('transaction_name_required'))
        if len(name.strip()) < 3:
            raise ValidationError(_('transaction_name_min_length'))
        return name.strip()
    
    def clean_from_party(self):
        """Validate from party field"""
        from_party = self.cleaned_data.get('from_party')
        if not from_party or not from_party.strip():
            raise ValidationError(_('transaction_from_party_required'))
        return from_party.strip()
    
    def clean_to_party(self):
        """Validate to party field"""
        to_party = self.cleaned_data.get('to_party')
        if not to_party or not to_party.strip():
            raise ValidationError(_('transaction_to_party_required'))
        return to_party.strip()
    
    def clean_amount(self):
        """Validate amount is positive"""
        amount = self.cleaned_data.get('amount')
        if amount is None:
            raise ValidationError(_('transaction_amount_required'))
        if amount <= 0:
            raise ValidationError(_('transaction_amount_positive'))
        return amount
    
    def clean(self):
        """Validate that the parties are different"""
        cleaned_data = super().clean()
        from_party = cleaned_data.get('from_party')
        to_party = cleaned_data.get('to_party')
        if from_party and to_party and from_party.lower() == to_party.lower():
            raise ValidationError(_('transaction_parties_same_error'))
        return cleaned_data


class DocumentsForm(forms.ModelForm):
    """Form for uploading/editing documents"""
    
    class Meta:
        model = Documents
        fields = ['name', 'file']
        error_messages = {
            'name': {'required': _('document_name_required')},
            'file': {'required': _('document_file_required')},
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._old_file_name = self.instance.file.name if self.instance.pk and self.instance.file else None
        
    def clean_name(self):
        """Validate name field"""
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise ValidationError(_('document_name_required'))
        if len(name.strip()) < 3:
            raise ValidationError(_('document_name_min_length'))
        return name.strip()
    
    def clean_file(self):
        """Validate extension, size and content of a newly uploaded file"""
        upload = self.cleaned_data.get('file')
        if not upload:
            raise ValidationError(_('document_file_required'))
        # An unchanged file on update is the stored FieldFile, which was validated on upload
        if not isinstance(upload, UploadedFile):
            return upload
        
        extension = upload.name.rsplit('.', 1)[-1].lower() if '.' in upload.name else ''
        if extension not in DOCUMENT_ALLOWED_EXTENSIONS:
            raise ValidationError(_('document_file_type_error'))
        if upload.size > DOCUMENT_MAX_FILE_SIZE:
            raise ValidationError(_('document_file_size_error'), params={'size': DOCUMENT_MAX_FILE_SIZE_MB})
        
        header = upload.read(16)
        upload.seek(0)
        if not any(header.startswith(signature) for signature in DOCUMENT_FILE_SIGNATURES[extension]):
            raise ValidationError(_('document_file_content_error'))
        return upload
    
    def save(self, commit=True):
        """Record file details and remove the replaced file from storage"""
        document = super().save(commit=False)
        upload = self.cleaned_data.get('file')
        is_new_upload = isinstance(upload, UploadedFile)
        if is_new_upload:
            document.original_filename = upload.name[:255]
            document.file_size = upload.size
        if commit:
            document.save()
            if is_new_upload and self._old_file_name:
                document.file.storage.delete(self._old_file_name)
        return document


class DataImportForm(forms.Form):
    """Form for uploading a JSON export file; cleaned_data['file'] is the parsed export payload"""
    file = forms.FileField(error_messages={'required': _('import_file_required')})
    replace_existing = forms.BooleanField(required=False)
    
    def clean_file(self):
        """Validate extension, size and structure of the export file"""
        upload = self.cleaned_data.get('file')
        if not upload:
            raise ValidationError(_('import_file_required'))
        if not upload.name.lower().endswith('.json'):
            raise ValidationError(_('import_file_type_error'))
        if upload.size > DATA_IMPORT_MAX_FILE_SIZE:
            raise ValidationError(_('import_file_size_error'), params={'size': DATA_IMPORT_MAX_FILE_SIZE_MB})
        
        try:
            payload = json.loads(upload.read().decode('utf-8-sig'))
        except (UnicodeDecodeError, ValueError):
            raise ValidationError(_('import_file_invalid_json'))
        
        if not isinstance(payload, dict) or payload.get('app') != DATA_EXPORT_APP_ID or not isinstance(payload.get('data'), dict):
            raise ValidationError(_('import_file_not_export'))
        if payload.get('version') != DATA_EXPORT_VERSION:
            raise ValidationError(_('import_file_version_error'))
        return payload
