FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -U pip && pip install -r requirements.txt
COPY app /app/app
ENV HF_HOME=/cache/hf
EXPOSE 8000
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]
