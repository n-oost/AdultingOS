# Backend Runbook

Virtual env (Windows)
```
cd C:\AdultingOS
.\venv\Scripts\Activate.ps1
```

Server
```
cd backend\adultingos_web
python manage.py runserver 127.0.0.1:8000
```

Migrations
```
python manage.py makemigrations
python manage.py migrate
```

Superuser (Django admin)
```
python manage.py createsuperuser
```

Database
- Ensure PostgreSQL service is running
- If connection fails: verify .env values and host/port
