from django import forms
from django.contrib.auth.models import User
from .models import Vehicle, TyreService, BatteryService, UserProfile
import re

def validate_name(value):
    if not value or not value[0].isupper():
        raise forms.ValidationError('Name must start with a capital letter.')
    if any(c.isdigit() for c in value):
        raise forms.ValidationError('Name must not contain numbers.')

def validate_number_plate(value):
    if not value.startswith('U'):
        raise forms.ValidationError('Number plate must start with U.')
    if not value.isalnum():
        raise forms.ValidationError('Number plate must be alphanumeric only.')
    if len(value) >= 8:
        raise forms.ValidationError('Number plate must be less than 8 characters.')

def validate_ugandan_phone(value):
    pattern = r'^(\+256|0)(7[0-9]|3[0-9])[0-9]{7}$'
    if not re.match(pattern, value):
        raise forms.ValidationError('Enter a valid Ugandan phone number (e.g. 0701234567).')

def validate_nin(value):
    if value:
        pattern = r'^(CM|CF|PM|PF)[0-9]{9}[A-Z]$'
        if not re.match(pattern, value.upper()):
            raise forms.ValidationError('NIN format: CM/CF/PM/PF + 9 digits + 1 letter (e.g. CM123456789A).')

WIDGET_CLASSES = {'class': 'form-control'}
SELECT_CLASSES = {'class': 'form-select'}

class VehicleRegisterForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['driver_name','vehicle_type','number_plate','vehicle_model',
                  'vehicle_color','phone_number','nin_number','arrival_time','notes']
        widgets = {
            'driver_name': forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. John Doe'}),
            'vehicle_type': forms.Select(attrs={'class':'form-select','id':'id_vehicle_type'}),
            'number_plate': forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. UAA123B'}),
            'vehicle_model': forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Toyota Corolla'}),
            'vehicle_color': forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Silver'}),
            'phone_number': forms.TextInput(attrs={'class':'form-control','placeholder':'0701234567'}),
            'nin_number': forms.TextInput(attrs={'class':'form-control','placeholder':'CM123456789A','id':'id_nin_number'}),
            'arrival_time': forms.DateTimeInput(attrs={'type':'datetime-local','class':'form-control'}),
            'notes': forms.Textarea(attrs={'class':'form-control','rows':2}),
        }

    def clean_driver_name(self):
        v = self.cleaned_data['driver_name']
        validate_name(v)
        return v

    def clean_number_plate(self):
        v = self.cleaned_data['number_plate'].upper()
        validate_number_plate(v)
        return v

    def clean_phone_number(self):
        v = self.cleaned_data['phone_number']
        validate_ugandan_phone(v)
        return v

    def clean_nin_number(self):
        v = self.cleaned_data.get('nin_number','')
        vtype = self.cleaned_data.get('vehicle_type','')
        if vtype == 'boda_boda' and not v:
            raise forms.ValidationError('NIN is required for Boda-boda.')
        if v:
            validate_nin(v)
        return v.upper() if v else v


class VehicleEditForm(VehicleRegisterForm):
    pass


class VehicleSignOutForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['receiver_name','receiver_phone','receiver_gender','receiver_nin']
        widgets = {
            'receiver_name': forms.TextInput(attrs={'class':'form-control','placeholder':'Full name'}),
            'receiver_phone': forms.TextInput(attrs={'class':'form-control','placeholder':'0701234567'}),
            'receiver_gender': forms.Select(choices=[('','-- Select --'),('Male','Male'),('Female','Female')],attrs={'class':'form-select'}),
            'receiver_nin': forms.TextInput(attrs={'class':'form-control','placeholder':'CM123456789A (optional)'}),
        }

    def clean_receiver_name(self):
        v = self.cleaned_data['receiver_name']
        validate_name(v)
        return v

    def clean_receiver_phone(self):
        v = self.cleaned_data['receiver_phone']
        validate_ugandan_phone(v)
        return v

    def clean_receiver_nin(self):
        v = self.cleaned_data.get('receiver_nin','')
        if v:
            validate_nin(v)
        return v.upper() if v else v


class TyreServiceForm(forms.ModelForm):
    class Meta:
        model = TyreService
        fields = ['customer_name','phone_number','vehicle_number_plate',
                  'service_type','tyre_size','quantity','unit_price','notes']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class':'form-control'}),
            'phone_number': forms.TextInput(attrs={'class':'form-control','placeholder':'0701234567'}),
            'vehicle_number_plate': forms.TextInput(attrs={'class':'form-control','placeholder':'Optional'}),
            'service_type': forms.Select(attrs={'class':'form-select','id':'id_service_type'}),
            'tyre_size': forms.Select(attrs={'class':'form-select'}),
            'quantity': forms.NumberInput(attrs={'class':'form-control','min':1}),
            'unit_price': forms.NumberInput(attrs={'class':'form-control','id':'id_unit_price','step':'100'}),
            'notes': forms.Textarea(attrs={'class':'form-control','rows':2}),
        }

    def clean_customer_name(self):
        v = self.cleaned_data['customer_name']
        validate_name(v)
        return v

    def clean_phone_number(self):
        v = self.cleaned_data['phone_number']
        validate_ugandan_phone(v)
        return v

    def clean_vehicle_number_plate(self):
        v = self.cleaned_data.get('vehicle_number_plate','').strip()
        if v:
            validate_number_plate(v.upper())
            return v.upper()
        return v


class BatteryServiceForm(forms.ModelForm):
    class Meta:
        model = BatteryService
        fields = ['customer_name','phone_number','vehicle_number_plate',
                  'transaction_type','battery_size','battery_brand',
                  'quantity','unit_price','deposit_amount',
                  'hire_duration_days','due_date','notes']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class':'form-control'}),
            'phone_number': forms.TextInput(attrs={'class':'form-control','placeholder':'0701234567'}),
            'vehicle_number_plate': forms.TextInput(attrs={'class':'form-control','placeholder':'Optional'}),
            'transaction_type': forms.Select(attrs={'class':'form-select','id':'id_trans_type'}),
            'battery_size': forms.Select(attrs={'class':'form-select'}),
            'battery_brand': forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Chloride Exide'}),
            'quantity': forms.NumberInput(attrs={'class':'form-control','min':1}),
            'unit_price': forms.NumberInput(attrs={'class':'form-control','step':'1000'}),
            'deposit_amount': forms.NumberInput(attrs={'class':'form-control','step':'1000'}),
            'hire_duration_days': forms.NumberInput(attrs={'class':'form-control','min':0,'id':'id_hire_days'}),
            'due_date': forms.DateInput(attrs={'type':'date','class':'form-control','id':'id_due_date'}),
            'notes': forms.Textarea(attrs={'class':'form-control','rows':2}),
        }

    def clean_customer_name(self):
        v = self.cleaned_data['customer_name']
        validate_name(v)
        return v

    def clean_phone_number(self):
        v = self.cleaned_data['phone_number']
        validate_ugandan_phone(v)
        return v


ROLE_CHOICES = [
    ('admin','System Admin'),
    ('attendant','Parking Attendant'),
    ('tyre_manager','Tyre Section Manager'),
    ('battery_manager','Battery Section Manager'),
]

class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class':'form-control'}))
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={'class':'form-select'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'0701234567'}))

    class Meta:
        model = User
        fields = ['username','first_name','last_name','email']
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control'}),
            'first_name': forms.TextInput(attrs={'class':'form-control'}),
            'last_name': forms.TextInput(attrs={'class':'form-control'}),
            'email': forms.EmailInput(attrs={'class':'form-control'}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('confirm_password'):
            raise forms.ValidationError('Passwords do not match.')
        return cleaned


class UserEditForm(forms.ModelForm):
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={'class':'form-select'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'form-control'}))

    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control'}),
            'first_name': forms.TextInput(attrs={'class':'form-control'}),
            'last_name': forms.TextInput(attrs={'class':'form-control'}),
            'email': forms.EmailInput(attrs={'class':'form-control'}),
        }
