FROM python:3.9-slim

# Установка системных зависимостей для компиляции psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

COPY tests/ ./tests/

EXPOSE 5000

# ВАЖНО: правильно указываем фабричный метод
CMD ["python", "-m", "flask", "--app", "app:create_app()", "run", "--host=0.0.0.0"]