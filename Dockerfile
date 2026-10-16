FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput || true

CMD ["sh", "-c", "gunicorn linkpay_api.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
