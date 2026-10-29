"""Constants for AssetsLiabilities app"""
from django.utils.translation import gettext_lazy as _


# Debt Asset Types
DEBT_ASSET_TYPE_BANK_ACCOUNT = 'bank_account'
DEBT_ASSET_TYPE_FD_RD = 'fd_rd'
DEBT_ASSET_TYPE_GOVT_SECURITIES = 'govt_securities'
DEBT_ASSET_TYPE_DEBT_MUTUAL_FUND = 'debt_mutual_fund'

DEBT_ASSET_TYPE_CHOICES = [
    (DEBT_ASSET_TYPE_BANK_ACCOUNT, _('debt_asset_type_bank_account')),
    (DEBT_ASSET_TYPE_FD_RD, _('debt_asset_type_fd_rd')),
    (DEBT_ASSET_TYPE_GOVT_SECURITIES, _('debt_asset_type_govt_securities')),
    (DEBT_ASSET_TYPE_DEBT_MUTUAL_FUND, _('debt_asset_type_debt_mutual_fund')),
]

# Stock Asset Types
STOCK_ASSET_TYPE_LARGE_CAP = 'large_cap'
STOCK_ASSET_TYPE_MID_CAP = 'mid_cap'
STOCK_ASSET_TYPE_SMALL_CAP = 'small_cap'

STOCK_ASSET_TYPE_CHOICES = [
    (STOCK_ASSET_TYPE_LARGE_CAP, _('stock_asset_type_large_cap')),
    (STOCK_ASSET_TYPE_MID_CAP, _('stock_asset_type_mid_cap')),
    (STOCK_ASSET_TYPE_SMALL_CAP, _('stock_asset_type_small_cap')),
]

# Gold Asset Types
GOLD_ASSET_TYPE_PHYSICAL = 'physical_gold'
GOLD_ASSET_TYPE_DIGITAL = 'digital_gold'
GOLD_ASSET_TYPE_SGB = 'gold_sgb'
GOLD_ASSET_TYPE_MUTUAL_FUND = 'gold_mutual_fund'

GOLD_ASSET_TYPE_CHOICES = [
    (GOLD_ASSET_TYPE_PHYSICAL, _('gold_asset_type_physical')),
    (GOLD_ASSET_TYPE_DIGITAL, _('gold_asset_type_digital')),
    (GOLD_ASSET_TYPE_SGB, _('gold_asset_type_sgb')),
    (GOLD_ASSET_TYPE_MUTUAL_FUND, _('gold_asset_type_mutual_fund')),
]

# Document Upload Rules
DOCUMENT_MAX_FILE_SIZE_MB = 5
DOCUMENT_MAX_FILE_SIZE = DOCUMENT_MAX_FILE_SIZE_MB * 1024 * 1024
DOCUMENT_ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpg', 'jpeg']

# File signatures (magic bytes) used to verify the content matches the extension
DOCUMENT_FILE_SIGNATURES = {
    'pdf': [b'%PDF-'],
    'png': [b'\x89PNG\r\n\x1a\n'],
    'jpg': [b'\xff\xd8\xff'],
    'jpeg': [b'\xff\xd8\xff'],
}

# Data Export / Import (JSON backup of assets, liabilities and transactions; documents excluded)
DATA_EXPORT_APP_ID = 'finance_manager'
DATA_EXPORT_VERSION = 1
DATA_IMPORT_MAX_FILE_SIZE_MB = 2
DATA_IMPORT_MAX_FILE_SIZE = DATA_IMPORT_MAX_FILE_SIZE_MB * 1024 * 1024
DATA_IMPORT_MAX_ERRORS_SHOWN = 20
