# Backend Environment (.env)

Location
- c:\AdultingOS\backend\adultingos_web\.env

Example (development)
```
DJANGO_SECRET_KEY=django-insecure-change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=adultingos
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-db-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

Notes
- Ensure settings.py loads .env (e.g., python-dotenv or os.environ)
- Never commit real secrets. Use separate values for prod.
