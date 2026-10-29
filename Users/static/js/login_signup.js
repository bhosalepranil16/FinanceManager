// Login/Signup - Tab Switching and Form Validation (jQuery)

/**
 * Switch between login and signup tabs
 * @param {string} tab - 'login' or 'signup'
 */
function showTab(tab) {
    if (tab === 'login') {
        $('#login-tab').addClass('active');
        $('#signup-tab').removeClass('active');
        $('#login-form').addClass('active');
        $('#signup-form').removeClass('active');
    } else {
        $('#signup-tab').addClass('active');
        $('#login-tab').removeClass('active');
        $('#signup-form').addClass('active');
        $('#login-form').removeClass('active');
    }
}

// Document ready - Initialize event handlers
$(document).ready(function() {
    // Form validation for mobile number - only allow digits
    $('#signup-mobile').on('input', function() {
        // Use \D instead of [^0-9] for better performance
        $(this).val($(this).val().replace(/\D/g, ''));
    });
    
    // Form validation for country code - "+" followed by 1 to 3 digits (rule comes from the input's pattern)
    $('#signup-country-code').on('input', function() {
        const digits = $(this).val().replace(/\D/g, '');
        $(this).val('+' + digits.slice(0, this.maxLength - 1));
        this.setCustomValidity(this.validity.patternMismatch ? gettext('user_country_code_invalid_format') : '');
    });
    
    // Optional: Add smooth transitions
    $('.auth-tab').on('click', function() {
        const tab = $(this).attr('id').replace('-tab', '');
        showTab(tab);
    });
});
