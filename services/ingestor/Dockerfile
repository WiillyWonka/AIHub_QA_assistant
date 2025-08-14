FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl unzip libglib2.0-0 libnss3 libgdk-pixbuf2.0-0 libgtk-3-0 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 xvfb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -U pip && pip install -r requirements.txt

# Установим браузеры Playwright для скачивания кнопкой
RUN python -m playwright install --with-deps chromium

COPY ../../scripts/playwright-download.py /app/scripts/playwright-download.py
COPY run.py /app/run.py

ENV DATA_DIR=/app/data
RUN mkdir -p ${DATA_DIR}/pdf

CMD ["python", "run.py"]
