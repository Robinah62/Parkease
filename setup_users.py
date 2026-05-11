from django.contrib.auth.models import User
from core.models import UserProfile

users = [
    {'username': 'admin',       'password': 'parkease2024', 'first': 'System',  'last': 'Admin',   'role': 'admin',           'super': True},
    {'username': 'attendant1',  'password': 'parkease2024', 'first': 'James',   'last': 'Okello',  'role': 'attendant',       'super': False},
    {'username': 'tyre_mgr',    'password': 'parkease2024', 'first': 'Sarah',   'last': 'Nakato',  'role': 'tyre_manager',    'super': False},
    {'username': 'battery_mgr', 'password': 'parkease2024', 'first': 'Peter',   'last': 'Ssempa',  'role': 'battery_manager', 'super': False},
]

for u in users:
    if not User.objects.filter(username=u['username']).exists():
        if u['super']:
            user = User.objects.create_superuser(u['username'], f"{u['username']}@parkease.ug", u['password'])
        else:
            user = User.objects.create_user(u['username'], f"{u['username']}@parkease.ug", u['password'])
        user.first_name = u['first']
        user.last_name  = u['last']
        user.save()
        UserProfile.objects.get_or_create(user=user, defaults={'role': u['role']})
        print(f"Created: {u['username']} ({u['role']})")
    else:
        print(f"Already exists: {u['username']}")

print("Done! All users ready.")
