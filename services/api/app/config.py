import os

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
COLLECTION = os.getenv("COLLECTION_NAME", "itmo_mai")
MODEL_QWEN = os.getenv("MODEL_QWEN", "Qwen/Qwen3-1.7B")
MAX_CTX_CHARS = 6000
TOP_K = 8
