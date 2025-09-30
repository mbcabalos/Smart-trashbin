from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Admin URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-users/', views.admin_users, name='admin_users'),
    path('admin-vouchers/', views.admin_vouchers, name='admin_vouchers'),
    path('admin-users/add/', views.admin_add_user, name='admin_add_user'),
    path('admin-users/edit/<str:user_id>/', views.admin_edit_user, name='admin_edit_user'),
    path('admin-users/delete/<str:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('admin-vouchers/add/', views.admin_add_voucher, name='admin_add_voucher'),
    path('admin-vouchers/delete/<str:voucher_id>/', views.admin_delete_voucher, name='admin_delete_voucher'),

    # Auth URLs
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),      # Custom login view
    path('logout/', views.logout_view, name='logout'),   # Custom logout view
]
