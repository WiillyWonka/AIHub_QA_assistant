import os

MODEL_QWEN = os.getenv("MODEL_QWEN", "Qwen/Qwen3-1.7B")
DATA_DIR = os.getenv("DATA_DIR", "/app/data")
ALLOWED_PROGRAMM = {"ai", "ai_product"}
