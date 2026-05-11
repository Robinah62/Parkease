from django.contrib import admin
from .models import Vehicle, TyreService, BatteryService, UserProfile

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['receipt_number','driver_name','number_plate','vehicle_type','status','parking_fee','arrival_time']
    list_filter = ['status','vehicle_type']
    search_fields = ['driver_name','number_plate','receipt_number']

@admin.register(TyreService)
class TyreAdmin(admin.ModelAdmin):
    list_display = ['receipt_number','customer_name','service_type','total_amount','date_time']
    search_fields = ['customer_name','receipt_number']

@admin.register(BatteryService)
class BatteryAdmin(admin.ModelAdmin):
    list_display = ['receipt_number','customer_name','transaction_type','battery_size','total_amount','date_time']
    search_fields = ['customer_name','receipt_number']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user','role','phone']
