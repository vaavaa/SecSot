# Используем официальную базовуюimage Python 3.11
FROM python:3.11-slim

# Установим необходимые зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
COPY ./app ./app

WORKDIR /app

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем бота при запуске контейнера
CMD ["python", "main_fresh.py"]