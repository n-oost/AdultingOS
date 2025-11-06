# Getting Started (Dev)

Prereqs
- Python 3.11+, Node 18+, Git, PostgreSQL (running)

Backend (Django)
- Windows PowerShell

```
cd C:\AdultingOS
# If you have a venv, activate it; otherwise create one
# python -m venv .\venv
.\venv\Scripts\Activate.ps1
cd backend\adultingos_web
python manage.py runserver 127.0.0.1:8000
```

Frontend (React web)
```
cd C:\AdultingOS\frontend
npm install
npm start
```

Health checks
- API: http://127.0.0.1:8000/api/
- Web: http://localhost:3000
