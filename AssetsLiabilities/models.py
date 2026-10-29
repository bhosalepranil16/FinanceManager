import os
import uuid

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .constants import DEBT_ASSET_TYPE_CHOICES, STOCK_ASSET_TYPE_CHOICES, GOLD_ASSET_TYPE_CHOICES


class DebtAssets(models.Model):
    """Debt assets tracking for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='debt_assets')
    name = models.CharField(max_length=100, help_text=_("debt_asset_name"))
    type = models.CharField(max_length=50, choices=DEBT_ASSET_TYPE_CHOICES, help_text=_("debt_asset_type"))
    amount = models.IntegerField(help_text=_("debt_asset_amount"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_type_display()} - {self.amount}"
    
    class Meta:
        verbose_name = _("debt_asset")
        verbose_name_plural = _("debt_assets")


class StockAssets(models.Model):
    """Stock assets tracking for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stock_assets')
    name = models.CharField(max_length=100, help_text=_("stock_asset_name"))
    type = models.CharField(max_length=50, choices=STOCK_ASSET_TYPE_CHOICES, help_text=_("stock_asset_type"))
    amount = models.IntegerField(help_text=_("stock_asset_amount"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.name} - {self.get_type_display()} - {self.amount}"
    
    class Meta:
        verbose_name = _("stock_asset")
        verbose_name_plural = _("stock_assets")


class MutualFundAssets(models.Model):
    """Mutual fund assets tracking for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mutual_fund_assets')
    name = models.CharField(max_length=100, help_text=_("mutual_fund_asset_name"))
    amount = models.IntegerField(help_text=_("mutual_fund_asset_amount"))
    large_cap_percentage = models.IntegerField(help_text=_("mutual_fund_large_cap_percentage"))
    mid_cap_percentage = models.IntegerField(help_text=_("mutual_fund_mid_cap_percentage"))
    small_cap_percentage = models.IntegerField(help_text=_("mutual_fund_small_cap_percentage"))
    debt_percentage = models.IntegerField(help_text=_("mutual_fund_debt_percentage"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        """Validate that all percentages sum to exactly 100"""
        percentages = [
            self.large_cap_percentage,
            self.mid_cap_percentage,
            self.small_cap_percentage,
            self.debt_percentage,
        ]
        # Missing percentages are reported as field errors by the form
        if any(percentage is None for percentage in percentages):
            return
        if sum(percentages) != 100:
            raise ValidationError(_('mutual_fund_percentage_sum_error'))
    
    def save(self, *args, **kwargs):
        """Override save to call clean validation"""
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.name} - {self.amount}"
    
    class Meta:
        verbose_name = _("mutual_fund_asset")
        verbose_name_plural = _("mutual_fund_assets")


class GoldAssets(models.Model):
    """Gold assets tracking for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gold_assets')
    name = models.CharField(max_length=100, help_text=_("gold_asset_name"))
    type = models.CharField(max_length=50, choices=GOLD_ASSET_TYPE_CHOICES, help_text=_("gold_asset_type"))
    amount = models.IntegerField(help_text=_("gold_asset_amount"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.name} - {self.get_type_display()} - {self.amount}"
    
    class Meta:
        verbose_name = _("gold_asset")
        verbose_name_plural = _("gold_assets")


class CryptoAssets(models.Model):
    """Cryptocurrency assets tracking for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crypto_assets')
    name = models.CharField(max_length=100, help_text=_("crypto_asset_name"))
    amount = models.IntegerField(help_text=_("crypto_asset_amount"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.name} - {self.amount}"
    
    class Meta:
        verbose_name = _("crypto_asset")
        verbose_name_plural = _("crypto_assets")


class RealEstateAssets(models.Model):
    """Real estate assets tracking for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='real_estate_assets')
    name = models.CharField(max_length=100, help_text=_("real_estate_asset_name"))
    amount = models.IntegerField(help_text=_("real_estate_asset_amount"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.name} - {self.amount}"
    
    class Meta:
        verbose_name = _("real_estate_asset")
        verbose_name_plural = _("real_estate_assets")


class Liabilities(models.Model):
    """Liabilities tracking for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liabilities')
    name = models.CharField(max_length=100, help_text=_("liability_name"))
    amount = models.IntegerField(help_text=_("liability_amount"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.name} - {self.amount}"
    
    class Meta:
        verbose_name = _("liability")
        verbose_name_plural = _("liabilities")


class Transactions(models.Model):
    """Money transfers and amounts owed between parties/accounts for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    name = models.CharField(max_length=100, help_text=_("transaction_name"))
    from_party = models.CharField(max_length=100, help_text=_("transaction_from_party"))
    to_party = models.CharField(max_length=100, help_text=_("transaction_to_party"))
    amount = models.IntegerField(help_text=_("transaction_amount"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.name} - {self.from_party} -> {self.to_party} - {self.amount}"
    
    class Meta:
        verbose_name = _("transaction")
        verbose_name_plural = _("transactions")
        ordering = ['-created_at']


def document_upload_path(instance, filename):
    """Store files under a per-user folder with a random name (original name is kept in the DB)"""
    extension = os.path.splitext(filename)[1].lower()
    return f"documents/user_{instance.user_id}/{uuid.uuid4().hex}{extension}"


class Documents(models.Model):
    """Important documents (insurance, certificates, etc.) uploaded by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=100, help_text=_("document_name"))
    file = models.FileField(upload_to=document_upload_path, help_text=_("document_file"))
    original_filename = models.CharField(max_length=255, help_text=_("document_original_filename"))
    file_size = models.PositiveIntegerField(help_text=_("document_file_size"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.name} - {self.original_filename}"
    
    class Meta:
        verbose_name = _("document")
        verbose_name_plural = _("documents")
        ordering = ['-created_at']


@receiver(post_delete, sender=Documents)
def delete_document_file(sender, instance, **kwargs):
    """Remove the stored file when a document row is deleted"""
    if instance.file:
        instance.file.delete(save=False)
