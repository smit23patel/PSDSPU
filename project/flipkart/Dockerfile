FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p instance

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Init DB then start gunicorn
CMD ["sh", "-c", "python -c 'from app import app, db, seed_data; \
  app.app_context().push(); db.create_all(); seed_data()' && \
  gunicorn --bind 0.0.0.0:5000 --workers 2 wsgi:app"]
