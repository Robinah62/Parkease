# ParkEase — Integrated Parking & Vehicle Services Management System

A Django-based web application for managing parking, tyre clinic, and battery hire services at Parkville.

## Project Info
- **Django Project:** `parkease`
- **Main App:** `core`

## Quick Setup

```bash
# 1. Create & activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate      # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py makemigrations
python manage.py migrate

# 4. Create all users
python manage.py shell < setup_users.py

# 5. Run server
python manage.py runserver
```

Then visit: http://127.0.0.1:8000

## Login Credentials
| Username       | Password      | Role                 |
|----------------|---------------|----------------------|
| admin          | parkease2024  | System Admin         |
| attendant1     | parkease2024  | Parking Attendant    |
| tyre_mgr       | parkease2024  | Tyre Section Manager |
| battery_mgr    | parkease2024  | Battery Section Mgr  |

## Pages & Features
- `/login/` — Login page
- `/dashboard/` — Overview with today's stats
- `/vehicles/` — Vehicle list (filter, search, paginate)
- `/vehicles/register/` — Register arriving vehicle
- `/vehicles/<id>/` — Vehicle detail
- `/vehicles/<id>/edit/` — Edit vehicle record
- `/vehicles/<id>/signout/` — Sign out vehicle + collect receiver info
- `/vehicles/<id>/receipt/` — Print receipt
- `/tyre/` — Tyre clinic services
- `/battery/` — Battery hire & sales
- `/reports/` — Daily revenue report (all sections)
- `/users/` — User management (admin only)

## Fee Calculation Logic
- **< 3 hours (short stay):** Truck 2k, Personal/Taxi 2k, Coaster 3k, Boda 1k
- **Daytime (6am–7pm):** Truck 5k, Personal/Taxi 3k, Coaster 4k, Boda 2k
- **Night (7pm–6am):** Truck 10k, Personal/Taxi 2k, Coaster 2k, Boda 2k

## GitHub Push
```bash
git init
git add .
git commit -m "Initial commit: ParkEase complete project"
git remote add origin https://github.com/YOUR_USERNAME/parkease.git
git push -u origin main
```
