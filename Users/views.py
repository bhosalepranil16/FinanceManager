import json

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.translation import gettext as _, ngettext
from django.views.decorators.http import require_http_methods

from AssetsLiabilities.constants import (
    DATA_IMPORT_MAX_ERRORS_SHOWN, DATA_IMPORT_MAX_FILE_SIZE, DATA_IMPORT_MAX_FILE_SIZE_MB
)
from AssetsLiabilities.data_transfer import export_user_data, import_user_data
from AssetsLiabilities.forms import DataImportForm
from .constants import COUNTRY_CODE_MAX_LENGTH, COUNTRY_CODE_PATTERN
from .forms import SignupProfileForm


def login_signup_view(request):
    """View for login and signup page"""
    if request.user.is_authenticated:
        return redirect('portfolio_overview')  # Redirect to portfolio overview if already logged in
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'login':
            return handle_login(request)
        elif form_type == 'signup':
            return handle_signup(request)
    
    context = {
        'country_code_pattern': COUNTRY_CODE_PATTERN,
        'country_code_max_length': COUNTRY_CODE_MAX_LENGTH,
    }
    return render(request, 'Users/login_signup.html', context)


def handle_login(request):
    """Handle login form submission"""
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        auth_login(request, user)
        messages.success(request, _('msg_login_success'))
        return redirect('portfolio_overview')
    else:
        messages.error(request, _('msg_login_invalid'))
        return redirect('login_signup')


def handle_signup(request):
    """Handle signup form submission"""
    username = request.POST.get('username')
    email = request.POST.get('email')
    password1 = request.POST.get('password1')
    password2 = request.POST.get('password2')
    
    # Validate profile fields (names, country code, mobile) before anything is saved
    profile_form = SignupProfileForm(request.POST)
    if not profile_form.is_valid():
        for field_errors in profile_form.errors.values():
            for error in field_errors:
                messages.error(request, error)
        return redirect('login_signup')
    
    # Validation
    if password1 != password2:
        messages.error(request, _('msg_signup_password_mismatch'))
        return redirect('login_signup')
    
    if User.objects.filter(username=username).exists():
        messages.error(request, _('msg_signup_username_exists'))
        return redirect('login_signup')
    
    if User.objects.filter(email=email).exists():
        messages.error(request, _('msg_signup_email_exists'))
        return redirect('login_signup')
    
    # Create user and profile together, so a failure never leaves an account without a profile
    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
        
        messages.success(request, _('msg_signup_success'))
        return redirect('login_signup')
        
    except Exception as e:
        messages.error(request, _('msg_signup_error') % {'error': str(e)})
        return redirect('login_signup')


def logout_view(request):
    """Handle user logout"""
    auth_logout(request)
    messages.success(request, _('msg_logout_success'))
    return redirect('login_signup')


def dashboard_view(request):
    """Dashboard view - redirects to portfolio overview"""
    return redirect('portfolio_overview')


@login_required(login_url='login_signup')
def profile_view(request):
    """User profile page with data export / import"""
    context = {
        'import_max_file_size': DATA_IMPORT_MAX_FILE_SIZE,
        'import_help_text': _('form_help_import_file') % {'size': DATA_IMPORT_MAX_FILE_SIZE_MB},
    }
    return render(request, 'Users/profile.html', context)


@login_required(login_url='login_signup')
@require_http_methods(["GET"])
def profile_export_view(request):
    """Download the user's assets, liabilities and transactions as a JSON file"""
    payload = export_user_data(request.user)
    filename = f'finance_manager_{request.user.username}_{timezone.localdate():%Y-%m-%d}.json'
    response = HttpResponse(
        json.dumps(payload, indent=2, ensure_ascii=False, cls=DjangoJSONEncoder),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required(login_url='login_signup')
@require_http_methods(["POST"])
def profile_import_view(request):
    """Create assets, liabilities and transactions from an uploaded JSON export file"""
    try:
        form = DataImportForm(request.POST, request.FILES)
        if not form.is_valid():
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        
        created, errors = import_user_data(
            request.user, form.cleaned_data['file'], form.cleaned_data['replace_existing']
        )
        if errors:
            details = errors[:DATA_IMPORT_MAX_ERRORS_SHOWN]
            hidden_count = len(errors) - len(details)
            if hidden_count:
                details.append(_('import_error_more') % {'count': hidden_count})
            summary = ngettext('import_error_records', 'import_error_records_plural', len(errors)) % {'count': len(errors)}
            return JsonResponse({'success': False, 'errors': {'file': [summary]}, 'details': details}, status=400)
        
        return JsonResponse({
            'success': True,
            'total': sum(item['count'] for item in created),
            'created': created
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
