from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from . import views

urlpatterns = [
    path('', views.login_signup_view, name='login_signup'),
    path('login/', views.login_signup_view, name='login'),
    path('signup/', views.login_signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # User Profile
    path('profile/', views.profile_view, name='user_profile'),
    path('profile/export/', views.profile_export_view, name='user_profile_export'),
    path('profile/import/', views.profile_import_view, name='user_profile_import'),
    
    # Forgot Password
    path('forgot-password/', auth_views.PasswordResetView.as_view(
        template_name='Users/password_reset.html',
        email_template_name='Users/password_reset_email.txt',
        subject_template_name='Users/password_reset_subject.txt',
        success_url=reverse_lazy('password_reset_done'),
    ), name='password_reset'),
    path('forgot-password/sent/', auth_views.PasswordResetDoneView.as_view(
        template_name='Users/password_reset_done.html',
    ), name='password_reset_done'),
    path('reset-password/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='Users/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete'),
    ), name='password_reset_confirm'),
    path('reset-password/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='Users/password_reset_complete.html',
    ), name='password_reset_complete'),
]
