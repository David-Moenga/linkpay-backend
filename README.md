# LinkPay Backend

Django REST Framework API for LinkPay.

## Local setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

The API will run at `http://127.0.0.1:8000`.

## Environment variables

Copy `.env.example` to `.env` (or export variables):

```bash
DJANGO_ENV=development
DJANGO_SECRET_KEY=change-me
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Demo data

Create an account through the frontend Register page, or use the API:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","email":"alice@test.com","password":"Strong!pass123","account_type":"individual"}'
```

## Tests

```bash
.venv/bin/python manage.py test
```

## Troubleshooting login

- If login fails with 401, make sure the user exists: run `python manage.py createsuperuser` or register first.
- If CORS errors appear in the browser, ensure `CORS_ALLOWED_ORIGINS` includes your frontend URL.
- The frontend must point to this backend via `NEXT_PUBLIC_API_BASE_URL`.
