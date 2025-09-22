from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('bottle/<int:pk>/', views.bottle_detail, name='bottle_detail'),
    
    # Admin URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-users/', views.admin_users, name='admin_users'),
    path('admin-bottles/', views.admin_bottles, name='admin_bottles'),
    path('admin-vouchers/', views.admin_vouchers, name='admin_vouchers'),
    path('admin-users/add/', views.admin_add_user, name='admin_add_user'),
    path('admin-users/edit/<int:user_id>/', views.admin_edit_user, name='admin_edit_user'),
    path('admin-users/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('admin-bottles/add/', views.admin_add_bottle, name='admin_add_bottle'),
    path('admin-bottles/edit/<int:bottle_id>/', views.admin_edit_bottle, name='admin_edit_bottle'),
    path('admin-bottles/delete/<int:bottle_id>/', views.admin_delete_bottle, name='admin_delete_bottle'),
    path('admin-vouchers/add/', views.admin_add_voucher, name='admin_add_voucher'),
    path('admin-vouchers/delete/<int:voucher_id>/', views.admin_delete_voucher, name='admin_delete_voucher'),
    
    # Auth URLs
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path(
    "logout/",
    auth_views.LogoutView.as_view(next_page="login"),
    name="logout"
),

]