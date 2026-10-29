from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re
from .constants import COUNTRY_CODE_PATTERN
from .models import UserAdditionalData


class UserAdditionalDataForm(forms.ModelForm):
    """Form for creating/editing user additional data"""
    
    class Meta:
        model = UserAdditionalData
        fields = ['user', 'first_name', 'last_name', 'country_code', 'mobile_number']
        
    def clean_first_name(self):
        """Validate first name"""
        first_name = self.cleaned_data.get('first_name')
        if not first_name or not first_name.strip():
            raise ValidationError(_('user_first_name_required'))
        if len(first_name.strip()) < 2:
            raise ValidationError(_('user_first_name_min_length'))
        if not re.match(r'^[a-zA-Z\s]+$', first_name.strip()):
            raise ValidationError(_('user_first_name_alpha_only'))
        return first_name.strip().title()
    
    def clean_last_name(self):
        """Validate last name"""
        last_name = self.cleaned_data.get('last_name')
        if not last_name or not last_name.strip():
            raise ValidationError(_('user_last_name_required'))
        if len(last_name.strip()) < 2:
            raise ValidationError(_('user_last_name_min_length'))
        if not re.match(r'^[a-zA-Z\s]+$', last_name.strip()):
            raise ValidationError(_('user_last_name_alpha_only'))
        return last_name.strip().title()
    
    def clean_country_code(self):
        """Validate country code"""
        country_code = self.cleaned_data.get('country_code')
        if not country_code or not country_code.strip():
            raise ValidationError(_('user_country_code_required'))
        # "+" followed by 1 to 3 digits, not starting with 0
        if not re.fullmatch(COUNTRY_CODE_PATTERN, country_code.strip()):
            raise ValidationError(_('user_country_code_invalid_format'))
        return country_code.strip()
    
    def clean_mobile_number(self):
        """Validate mobile number is exactly 10 digits"""
        mobile_number = self.cleaned_data.get('mobile_number')
        if not mobile_number or not mobile_number.strip():
            raise ValidationError(_('user_mobile_number_required'))
        
        # Remove any spaces or special characters
        mobile_number = re.sub(r'\D', '', mobile_number)
        
        if len(mobile_number) != 10:
            raise ValidationError(_('user_mobile_number_length_error'))
        
        if not mobile_number.isdigit():
            raise ValidationError(_('user_mobile_number_digits_only'))
        
        return mobile_number


class SignupProfileForm(UserAdditionalDataForm):
    """Profile fields of the signup form; the user is attached after the account is created"""
    
    class Meta(UserAdditionalDataForm.Meta):
        fields = ['first_name', 'last_name', 'country_code', 'mobile_number']
