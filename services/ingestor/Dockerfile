FROM python:3.11-bookworm

RUN apt-get update && apt-get install -y poppler-utils\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -U pip && pip install -r requirements.txt

# Установим браузеры Playwright для скачивания кнопкой
RUN python -m playwright install --with-deps chromium

COPY playwright-download.py /app/scripts/playwright-download.py
COPY run.py /app/run.py

ENV DATA_DIR=/app/data
RUN mkdir -p ${DATA_DIR}/pdf

CMD ["python", "run.py"]
