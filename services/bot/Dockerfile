FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -U pip && pip install -r requirements.txt
COPY bot.py /app/bot.py
CMD ["python", "bot.py"]
