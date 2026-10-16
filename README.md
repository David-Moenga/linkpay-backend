# LinkPay Backend

Django REST Framework API for LinkPay.

## Local setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
DJANGO_ENV=development .venv/bin/python manage.py runserver
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

- `DJANGO_ENV` turns debug mode on and off (`development`/`dev` enable it). It defaults to `production`, which is the safe setting for every hosted deployment.
- `DJANGO_SECRET_KEY` signs the authentication tokens. Always set a real secret in production; the app warns and falls back to an insecure development key when it is missing.
- `DJANGO_ALLOWED_HOSTS` lists the hosts the API accepts (comma separated). On Railway this is the public domain of the service, e.g. `linkpay-backend.up.railway.app`.
- `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` must include the frontend origin, e.g. `https://linkpay.vendas.co.ke`.
- `DATABASE_URL` points at Postgres. When it is missing, Django falls back to SQLite.

## Demo data

Create an account through the frontend Register page, or use the API:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","email":"alice@test.com","password":"Strong!pass123","account_type":"individual"}'
```

## Deploying to Railway

The backend ships with a `Dockerfile`, so Railway builds and runs it automatically.

1. Push this repository to GitHub (or connect the repository in the Railway dashboard).
2. In the Railway dashboard, create a new project and add this repository, or run `railway link` from this directory and then `railway up`.
3. Add a **Postgres** plugin to the service (Dashboard -> your service -> Settings -> Add plugin). Railway then provides a `DATABASE_URL` variable automatically.
4. Set the environment variables for the service (Dashboard -> Variables, or `railway variables set`):
   ```bash
   DJANGO_SECRET_KEY=<generated secret key>
   DJANGO_ALLOWED_HOSTS=<service public domain, e.g. linkpay-backend.up.railway.app>
   CORS_ALLOWED_ORIGINS=https://linkpay.vendas.co.ke
   CSRF_TRUSTED_ORIGINS=https://linkpay.vendas.co.ke
   ```
   If Postgres was added, `DATABASE_URL` is set for you. Without it, Django falls back to SQLite.
5. Deploy. Railway assigns a public domain such as `https://linkpay-backend.up.railway.app`; list it in `DJANGO_ALLOWED_HOSTS` and share the frontend origin in `CORS_ALLOWED_ORIGINS`.

## Tests

```bash
.venv/bin/python manage.py test
```

## Troubleshooting login

- If login fails with 401, make sure the user exists: run `python manage.py createsuperuser` or register first.
- If CORS errors appear in the browser, ensure `CORS_ALLOWED_ORIGINS` includes your frontend URL.
- The frontend must point to this backend via `NEXT_PUBLIC_API_BASE_URL`.
