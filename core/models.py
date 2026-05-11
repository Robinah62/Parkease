from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random, string


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'System Admin'),
        ('attendant', 'Parking Attendant'),
        ('tyre_manager', 'Tyre Section Manager'),
        ('battery_manager', 'Battery Section Manager'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='attendant')
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('truck', 'Truck'),
        ('personal_car', 'Personal Car'),
        ('taxi', 'Taxi'),
        ('coaster', 'Coaster'),
        ('boda_boda', 'Boda-Boda'),
    ]
    STATUS_CHOICES = [
        ('parked', 'Parked'),
        ('signed_out', 'Signed Out'),
    ]
    receipt_number = models.CharField(max_length=20, unique=True, editable=False)
    driver_name = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    number_plate = models.CharField(max_length=10)
    vehicle_model = models.CharField(max_length=100)
    vehicle_color = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    nin_number = models.CharField(max_length=20, blank=True)
    arrival_time = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='parked')
    registered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='registered_vehicles')
    parking_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    signout_time = models.DateTimeField(null=True, blank=True)
    receiver_name = models.CharField(max_length=100, blank=True)
    receiver_phone = models.CharField(max_length=15, blank=True)
    receiver_gender = models.CharField(max_length=10, blank=True)
    receiver_nin = models.CharField(max_length=20, blank=True)
    signed_out_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='signedout_vehicles')

    class Meta:
        ordering = ['-arrival_time']

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = 'PKE' + ''.join(random.choices(string.digits, k=6))
        super().save(*args, **kwargs)

    def calculate_fee(self, signout_time=None):
        arrival = self.arrival_time
        checkout = signout_time or timezone.now()
        duration_hours = (checkout - arrival).total_seconds() / 3600
        hour = arrival.hour
        is_day = 6 <= hour <= 18
        is_short = duration_hours < 3
        rates = {
            'truck':        {'day': 5000, 'night': 10000, 'short': 2000},
            'personal_car': {'day': 3000, 'night': 2000,  'short': 2000},
            'taxi':         {'day': 3000, 'night': 2000,  'short': 2000},
            'coaster':      {'day': 4000, 'night': 2000,  'short': 3000},
            'boda_boda':    {'day': 2000, 'night': 2000,  'short': 1000},
        }
        r = rates.get(self.vehicle_type)
        if not r:
            return 0
        if is_short:
            return r['short']
        elif is_day:
            return r['day']
        else:
            return r['night']

    def get_duration(self):
        end = self.signout_time or timezone.now()
        delta = end - self.arrival_time
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        return f"{hours}h {minutes}m"

    def __str__(self):
        return f"{self.number_plate} - {self.driver_name} ({self.receipt_number})"


class TyreService(models.Model):
    SERVICE_TYPES = [
        ('pressure', 'Pressure Check'),
        ('puncture', 'Puncture Fixing'),
        ('valve', 'Valve Replacement'),
        ('tyre_sale', 'Tyre Sale'),
    ]
    TYRE_SIZES = [
        ('155/70R13', '155/70R13'), ('165/70R14', '165/70R14'),
        ('175/65R14', '175/65R14'), ('185/65R15', '185/65R15'),
        ('195/65R15', '195/65R15'), ('205/55R16', '205/55R16'),
        ('215/65R16', '215/65R16'), ('225/45R17', '225/45R17'),
        ('other', 'Other'),
    ]
    receipt_number = models.CharField(max_length=20, unique=True, editable=False)
    customer_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    vehicle_number_plate = models.CharField(max_length=10, blank=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    tyre_size = models.CharField(max_length=20, choices=TYRE_SIZES, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_time = models.DateTimeField(default=timezone.now)
    served_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = 'TYR' + ''.join(random.choices(string.digits, k=6))
        self.total_amount = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.receipt_number} - {self.customer_name}"

    class Meta:
        ordering = ['-date_time']


class BatteryService(models.Model):
    TRANSACTION_TYPES = [
        ('hire', 'Battery Hire'),
        ('sale', 'Battery Sale'),
        ('return', 'Battery Return'),
    ]
    BATTERY_SIZES = [
        ('35Ah','35Ah'),('45Ah','45Ah'),('60Ah','60Ah'),
        ('75Ah','75Ah'),('100Ah','100Ah'),('120Ah','120Ah'),('150Ah','150Ah'),
    ]
    receipt_number = models.CharField(max_length=20, unique=True, editable=False)
    customer_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    vehicle_number_plate = models.CharField(max_length=10, blank=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    battery_size = models.CharField(max_length=20, choices=BATTERY_SIZES)
    battery_brand = models.CharField(max_length=100, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    hire_duration_days = models.PositiveIntegerField(default=0)
    due_date = models.DateField(null=True, blank=True)
    returned = models.BooleanField(default=False)
    date_time = models.DateTimeField(default=timezone.now)
    served_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = 'BAT' + ''.join(random.choices(string.digits, k=6))
        self.total_amount = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.receipt_number} - {self.customer_name}"

    class Meta:
        ordering = ['-date_time']
