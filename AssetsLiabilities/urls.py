from django.urls import path
from . import views

urlpatterns = [
    # Portfolio Overview
    path('portfolio/', views.portfolio_overview, name='portfolio_overview'),
    
    # Debt Assets
    path('debt-assets/', views.debt_assets_list, name='debt_assets_list'),
    path('debt-assets/create/', views.debt_assets_create, name='debt_assets_create'),
    path('debt-assets/<int:pk>/', views.debt_assets_detail, name='debt_assets_detail'),
    path('debt-assets/<int:pk>/update/', views.debt_assets_update, name='debt_assets_update'),
    path('debt-assets/<int:pk>/delete/', views.debt_assets_delete, name='debt_assets_delete'),
    
    # Stock Assets
    path('stock-assets/', views.stock_assets_list, name='stock_assets_list'),
    path('stock-assets/create/', views.stock_assets_create, name='stock_assets_create'),
    path('stock-assets/<int:pk>/', views.stock_assets_detail, name='stock_assets_detail'),
    path('stock-assets/<int:pk>/update/', views.stock_assets_update, name='stock_assets_update'),
    path('stock-assets/<int:pk>/delete/', views.stock_assets_delete, name='stock_assets_delete'),
    
    # Mutual Funds
    path('mutual-funds/', views.mutual_fund_list, name='mutual_fund_list'),
    path('mutual-funds/create/', views.mutual_fund_create, name='mutual_fund_create'),
    path('mutual-funds/<int:pk>/', views.mutual_fund_detail, name='mutual_fund_detail'),
    path('mutual-funds/<int:pk>/update/', views.mutual_fund_update, name='mutual_fund_update'),
    path('mutual-funds/<int:pk>/delete/', views.mutual_fund_delete, name='mutual_fund_delete'),
    
    # Gold Assets
    path('gold-assets/', views.gold_assets_list, name='gold_assets_list'),
    path('gold-assets/create/', views.gold_assets_create, name='gold_assets_create'),
    path('gold-assets/<int:pk>/', views.gold_assets_detail, name='gold_assets_detail'),
    path('gold-assets/<int:pk>/update/', views.gold_assets_update, name='gold_assets_update'),
    path('gold-assets/<int:pk>/delete/', views.gold_assets_delete, name='gold_assets_delete'),
    
    # Crypto Assets
    path('crypto-assets/', views.crypto_assets_list, name='crypto_assets_list'),
    path('crypto-assets/create/', views.crypto_assets_create, name='crypto_assets_create'),
    path('crypto-assets/<int:pk>/', views.crypto_assets_detail, name='crypto_assets_detail'),
    path('crypto-assets/<int:pk>/update/', views.crypto_assets_update, name='crypto_assets_update'),
    path('crypto-assets/<int:pk>/delete/', views.crypto_assets_delete, name='crypto_assets_delete'),
    
    # Real Estate
    path('real-estate/', views.real_estate_list, name='real_estate_list'),
    path('real-estate/create/', views.real_estate_create, name='real_estate_create'),
    path('real-estate/<int:pk>/', views.real_estate_detail, name='real_estate_detail'),
    path('real-estate/<int:pk>/update/', views.real_estate_update, name='real_estate_update'),
    path('real-estate/<int:pk>/delete/', views.real_estate_delete, name='real_estate_delete'),
    
    # Liabilities
    path('liabilities/', views.liabilities_list, name='liabilities_list'),
    path('liabilities/create/', views.liabilities_create, name='liabilities_create'),
    path('liabilities/<int:pk>/', views.liabilities_detail, name='liabilities_detail'),
    path('liabilities/<int:pk>/update/', views.liabilities_update, name='liabilities_update'),
    path('liabilities/<int:pk>/delete/', views.liabilities_delete, name='liabilities_delete'),
    
    # Transactions
    path('transactions/', views.transactions_list, name='transactions_list'),
    path('transactions/create/', views.transactions_create, name='transactions_create'),
    path('transactions/<int:pk>/', views.transactions_detail, name='transactions_detail'),
    path('transactions/<int:pk>/update/', views.transactions_update, name='transactions_update'),
    path('transactions/<int:pk>/delete/', views.transactions_delete, name='transactions_delete'),
    
    # Documents
    path('documents/', views.documents_list, name='documents_list'),
    path('documents/create/', views.documents_create, name='documents_create'),
    path('documents/<int:pk>/', views.documents_detail, name='documents_detail'),
    path('documents/<int:pk>/update/', views.documents_update, name='documents_update'),
    path('documents/<int:pk>/delete/', views.documents_delete, name='documents_delete'),
    path('documents/<int:pk>/file/', views.documents_file, name='documents_file'),
]

