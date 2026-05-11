from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_redirect, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # Vehicles
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/register/', views.vehicle_register, name='vehicle_register'),
    path('vehicles/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('vehicles/<int:pk>/edit/', views.vehicle_edit, name='vehicle_edit'),
    path('vehicles/<int:pk>/delete/', views.vehicle_delete, name='vehicle_delete'),
    path('vehicles/<int:pk>/signout/', views.vehicle_signout, name='vehicle_signout'),
    path('vehicles/<int:pk>/receipt/', views.vehicle_receipt, name='vehicle_receipt'),
    # Tyre
    path('tyre/', views.tyre_list, name='tyre_list'),
    path('tyre/add/', views.tyre_add, name='tyre_add'),
    path('tyre/<int:pk>/edit/', views.tyre_edit, name='tyre_edit'),
    path('tyre/<int:pk>/delete/', views.tyre_delete, name='tyre_delete'),
    # Battery
    path('battery/', views.battery_list, name='battery_list'),
    path('battery/add/', views.battery_add, name='battery_add'),
    path('battery/<int:pk>/edit/', views.battery_edit, name='battery_edit'),
    path('battery/<int:pk>/delete/', views.battery_delete, name='battery_delete'),
    # Reports
    path('reports/', views.reports, name='reports'),
    # Users
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_add, name='user_add'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
]
