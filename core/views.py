from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q
from datetime import date

from .models import Vehicle, TyreService, BatteryService, UserProfile
from .forms import (
    VehicleRegisterForm, VehicleSignOutForm, VehicleEditForm,
    TyreServiceForm, BatteryServiceForm, UserCreateForm, UserEditForm
)

# ── Helpers ──────────────────────────────────────────────────────────────────

def get_role(user):
    try:
        return user.profile.role
    except Exception:
        return 'attendant'

def is_admin(user):
    return get_role(user) == 'admin' or user.is_superuser

# ── Auth ─────────────────────────────────────────────────────────────────────

def home_redirect(request):
    return redirect('dashboard') if request.user.is_authenticated else redirect('login')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username','').strip(),
                            password=request.POST.get('password',''))
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'dashboard'))
        messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# ── Dashboard ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    today = date.today()
    parked = Vehicle.objects.filter(status='parked')
    signed_today = Vehicle.objects.filter(status='signed_out', signout_time__date=today)
    tyre_today = TyreService.objects.filter(date_time__date=today)
    bat_today = BatteryService.objects.filter(date_time__date=today)
    park_rev = signed_today.aggregate(t=Sum('parking_fee'))['t'] or 0
    tyre_rev = tyre_today.aggregate(t=Sum('total_amount'))['t'] or 0
    bat_rev = bat_today.aggregate(t=Sum('total_amount'))['t'] or 0
    return render(request, 'dashboard.html', {
        'currently_parked': parked.count(),
        'signed_out_today': signed_today.count(),
        'parking_revenue_today': park_rev,
        'tyre_revenue_today': tyre_rev,
        'battery_revenue_today': bat_rev,
        'total_revenue_today': park_rev + tyre_rev + bat_rev,
        'recent_vehicles': Vehicle.objects.order_by('-arrival_time')[:8],
        'role': get_role(request.user),
        'today': today,
    })

# ── Vehicles ─────────────────────────────────────────────────────────────────

@login_required
def vehicle_list(request):
    status_f = request.GET.get('status', 'parked')
    date_f = request.GET.get('date', '')
    search = request.GET.get('search', '').strip()
    qs = Vehicle.objects.all()
    if status_f:
        qs = qs.filter(status=status_f)
    if date_f:
        qs = qs.filter(arrival_time__date=date_f)
    if search:
        qs = qs.filter(Q(driver_name__icontains=search)|Q(number_plate__icontains=search)|Q(receipt_number__icontains=search))
    return render(request, 'vehicles/list.html', {
        'vehicles': qs, 'status_filter': status_f, 'date_filter': date_f,
        'search': search, 'role': get_role(request.user),
    })

@login_required
def vehicle_register(request):
    if request.method == 'POST':
        form = VehicleRegisterForm(request.POST)
        if form.is_valid():
            v = form.save(commit=False)
            v.registered_by = request.user
            v.parking_fee = v.calculate_fee()
            v.save()
            messages.success(request, f'Vehicle {v.number_plate} registered. Receipt: {v.receipt_number}')
            return redirect('vehicle_detail', pk=v.pk)
    else:
        form = VehicleRegisterForm()
    return render(request, 'vehicles/register.html', {'form': form, 'role': get_role(request.user)})

@login_required
def vehicle_detail(request, pk):
    v = get_object_or_404(Vehicle, pk=pk)
    return render(request, 'vehicles/detail.html', {'vehicle': v, 'role': get_role(request.user)})

@login_required
def vehicle_edit(request, pk):
    v = get_object_or_404(Vehicle, pk=pk)
    if v.status == 'signed_out':
        messages.error(request, 'Cannot edit a signed-out vehicle.')
        return redirect('vehicle_detail', pk=pk)
    if request.method == 'POST':
        form = VehicleEditForm(request.POST, instance=v)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle record updated.')
            return redirect('vehicle_detail', pk=pk)
    else:
        form = VehicleEditForm(instance=v)
    return render(request, 'vehicles/edit.html', {'form': form, 'vehicle': v, 'role': get_role(request.user)})

@login_required
def vehicle_delete(request, pk):
    v = get_object_or_404(Vehicle, pk=pk)
    if not is_admin(request.user):
        messages.error(request, 'Only admins can delete vehicle records.')
        return redirect('vehicle_detail', pk=pk)
    if request.method == 'POST':
        plate = v.number_plate
        v.delete()
        messages.success(request, f'Vehicle {plate} deleted.')
        return redirect('vehicle_list')
    return render(request, 'vehicles/delete_confirm.html', {'vehicle': v, 'role': get_role(request.user)})

@login_required
def vehicle_signout(request, pk):
    v = get_object_or_404(Vehicle, pk=pk)
    if v.status == 'signed_out':
        messages.info(request, 'This vehicle has already been signed out.')
        return redirect('vehicle_receipt', pk=pk)
    if request.method == 'POST':
        form = VehicleSignOutForm(request.POST, instance=v)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.signout_time = timezone.now()
            obj.status = 'signed_out'
            obj.parking_fee = obj.calculate_fee(signout_time=obj.signout_time)
            obj.signed_out_by = request.user
            obj.save()
            messages.success(request, f'Vehicle signed out. Fee: UGX {obj.parking_fee:,.0f}')
            return redirect('vehicle_receipt', pk=obj.pk)
    else:
        form = VehicleSignOutForm(instance=v)
    return render(request, 'vehicles/signout.html', {
        'form': form, 'vehicle': v,
        'estimated_fee': v.calculate_fee(),
        'role': get_role(request.user),
    })

@login_required
def vehicle_receipt(request, pk):
    v = get_object_or_404(Vehicle, pk=pk)
    return render(request, 'receipts/receipt.html', {'vehicle': v, 'role': get_role(request.user)})

# ── Tyre ─────────────────────────────────────────────────────────────────────

@login_required
def tyre_list(request):
    search = request.GET.get('search','').strip()
    date_f = request.GET.get('date','')
    qs = TyreService.objects.all()
    if search:
        qs = qs.filter(Q(customer_name__icontains=search)|Q(vehicle_number_plate__icontains=search)|Q(receipt_number__icontains=search))
    if date_f:
        qs = qs.filter(date_time__date=date_f)
    today_total = TyreService.objects.filter(date_time__date=date.today()).aggregate(t=Sum('total_amount'))['t'] or 0
    return render(request, 'tyre/list.html', {
        'services': qs, 'search': search, 'date_filter': date_f,
        'today_total': today_total, 'role': get_role(request.user),
    })

@login_required
def tyre_add(request):
    if request.method == 'POST':
        form = TyreServiceForm(request.POST)
        if form.is_valid():
            s = form.save(commit=False)
            s.served_by = request.user
            s.save()
            messages.success(request, f'Tyre service recorded. Receipt: {s.receipt_number}')
            return redirect('tyre_list')
    else:
        form = TyreServiceForm()
    return render(request, 'tyre/form.html', {'form': form, 'title': 'Add Tyre Service', 'role': get_role(request.user)})

@login_required
def tyre_edit(request, pk):
    s = get_object_or_404(TyreService, pk=pk)
    if request.method == 'POST':
        form = TyreServiceForm(request.POST, instance=s)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tyre service updated.')
            return redirect('tyre_list')
    else:
        form = TyreServiceForm(instance=s)
    return render(request, 'tyre/form.html', {'form': form, 'title': 'Edit Tyre Service', 'service': s, 'role': get_role(request.user)})

@login_required
def tyre_delete(request, pk):
    s = get_object_or_404(TyreService, pk=pk)
    if request.method == 'POST':
        s.delete()
        messages.success(request, 'Tyre service record deleted.')
        return redirect('tyre_list')
    return render(request, 'tyre/delete_confirm.html', {'service': s, 'role': get_role(request.user)})

# ── Battery ──────────────────────────────────────────────────────────────────

@login_required
def battery_list(request):
    search = request.GET.get('search','').strip()
    date_f = request.GET.get('date','')
    qs = BatteryService.objects.all()
    if search:
        qs = qs.filter(Q(customer_name__icontains=search)|Q(receipt_number__icontains=search))
    if date_f:
        qs = qs.filter(date_time__date=date_f)
    today_total = BatteryService.objects.filter(date_time__date=date.today()).aggregate(t=Sum('total_amount'))['t'] or 0
    return render(request, 'battery/list.html', {
        'services': qs, 'search': search, 'date_filter': date_f,
        'today_total': today_total, 'role': get_role(request.user),
    })

@login_required
def battery_add(request):
    if request.method == 'POST':
        form = BatteryServiceForm(request.POST)
        if form.is_valid():
            s = form.save(commit=False)
            s.served_by = request.user
            s.save()
            messages.success(request, f'Battery transaction recorded. Receipt: {s.receipt_number}')
            return redirect('battery_list')
    else:
        form = BatteryServiceForm()
    return render(request, 'battery/form.html', {'form': form, 'title': 'Add Battery Transaction', 'role': get_role(request.user)})

@login_required
def battery_edit(request, pk):
    s = get_object_or_404(BatteryService, pk=pk)
    if request.method == 'POST':
        form = BatteryServiceForm(request.POST, instance=s)
        if form.is_valid():
            form.save()
            messages.success(request, 'Battery transaction updated.')
            return redirect('battery_list')
    else:
        form = BatteryServiceForm(instance=s)
    return render(request, 'battery/form.html', {'form': form, 'title': 'Edit Battery Transaction', 'service': s, 'role': get_role(request.user)})

@login_required
def battery_delete(request, pk):
    s = get_object_or_404(BatteryService, pk=pk)
    if request.method == 'POST':
        s.delete()
        messages.success(request, 'Battery transaction deleted.')
        return redirect('battery_list')
    return render(request, 'battery/delete_confirm.html', {'service': s, 'role': get_role(request.user)})

# ── Reports ──────────────────────────────────────────────────────────────────

@login_required
def reports(request):
    from datetime import date as dt
    rd = request.GET.get('date', dt.today().isoformat())
    try:
        report_date = dt.fromisoformat(rd)
    except ValueError:
        report_date = dt.today()
    signed_out = Vehicle.objects.filter(status='signed_out', signout_time__date=report_date)
    tyre_svc = TyreService.objects.filter(date_time__date=report_date)
    bat_svc = BatteryService.objects.filter(date_time__date=report_date)
    park_rev = signed_out.aggregate(t=Sum('parking_fee'))['t'] or 0
    tyre_rev = tyre_svc.aggregate(t=Sum('total_amount'))['t'] or 0
    bat_rev = bat_svc.aggregate(t=Sum('total_amount'))['t'] or 0
    breakdown = {}
    for v in signed_out:
        vt = v.get_vehicle_type_display()
        if vt not in breakdown:
            breakdown[vt] = {'count': 0, 'revenue': 0}
        breakdown[vt]['count'] += 1
        breakdown[vt]['revenue'] += float(v.parking_fee)
    return render(request, 'reports/daily.html', {
        'report_date': report_date,
        'signed_out': signed_out,
        'tyre_services': tyre_svc,
        'battery_services': bat_svc,
        'parking_revenue': park_rev,
        'tyre_revenue': tyre_rev,
        'battery_revenue': bat_rev,
        'total_revenue': park_rev + tyre_rev + bat_rev,
        'vehicle_breakdown': breakdown,
        'role': get_role(request.user),
    })

# ── Users ────────────────────────────────────────────────────────────────────

@login_required
def user_list(request):
    if not is_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    users = User.objects.select_related('profile').all().order_by('username')
    return render(request, 'users/list.html', {'users': users, 'role': get_role(request.user)})

@login_required
def user_add(request):
    if not is_admin(request.user):
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            UserProfile.objects.create(user=user, role=form.cleaned_data['role'], phone=form.cleaned_data.get('phone',''))
            messages.success(request, f'User {user.username} created successfully.')
            return redirect('user_list')
    else:
        form = UserCreateForm()
    return render(request, 'users/form.html', {'form': form, 'title': 'Add User', 'role': get_role(request.user)})

@login_required
def user_edit(request, pk):
    if not is_admin(request.user):
        return redirect('dashboard')
    target = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=target)
        if form.is_valid():
            user = form.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = form.cleaned_data['role']
            profile.phone = form.cleaned_data.get('phone','')
            profile.save()
            messages.success(request, 'User updated successfully.')
            return redirect('user_list')
    else:
        try:
            initial = {'role': target.profile.role, 'phone': target.profile.phone}
        except Exception:
            initial = {}
        form = UserEditForm(instance=target, initial=initial)
    return render(request, 'users/form.html', {'form': form, 'title': 'Edit User', 'target_user': target, 'role': get_role(request.user)})

@login_required
def user_delete(request, pk):
    if not is_admin(request.user):
        return redirect('dashboard')
    target = get_object_or_404(User, pk=pk)
    if target == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('user_list')
    if request.method == 'POST':
        target.delete()
        messages.success(request, 'User deleted.')
        return redirect('user_list')
    return render(request, 'users/delete_confirm.html', {'target_user': target, 'role': get_role(request.user)})
