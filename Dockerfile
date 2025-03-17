FROM python:3.10-slim-buster

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV STRIPE_API_KEY=${STRIPE_API_KEY}
ENV TWILIO_ACCOUNT_SID = ${TWILIO_ACCOUNT_SID}
ENV TWILIO_AUTH_TOKEN = ${TWILIO_AUTH_TOKEN}


EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]