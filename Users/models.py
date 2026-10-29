from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class UserAdditionalData(models.Model):
    """Additional user data with one-to-one relationship to User model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, help_text=_("user_first_name"))
    last_name = models.CharField(max_length=50, help_text=_("user_last_name"))
    country_code = models.CharField(max_length=5, default="+91", help_text=_("user_country_code"))
    mobile_number = models.CharField(max_length=10, help_text=_("user_mobile_number"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.username})"
    
    class Meta:
        verbose_name = _("user_additional_data")
        verbose_name_plural = _("users_additional_data")
