import os, json, re, glob
import pdfplumber
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from uuid import uuid4

DATA_DIR = os.getenv("DATA_DIR", "/app/data")
PDF_DIR = os.path.join(DATA_DIR, "pdf")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.getenv("COLLECTION_NAME", "itmo_mai")
URL_AI = os.getenv("PROGRAM_URL_AI")
URL_AIP = os.getenv("PROGRAM_URL_AIPROD")

def ensure_pdf():
    paths = []
    if not os.path.exists(os.path.join(PDF_DIR, "ai.pdf")):
        os.system(f"python /app/scripts/playwright-download.py {URL_AI} {PDF_DIR} ai")
    if not os.path.exists(os.path.join(PDF_DIR, "ai_product.pdf")):
        os.system(f"python /app/scripts/playwright-download.py {URL_AIP} {PDF_DIR} ai_product")
    for x in ("ai.pdf","ai_product.pdf"):
        p = os.path.join(PDF_DIR, x)
        if os.path.exists(p):
            paths.append(p)
    return paths

def read_pdf_text(path):
    text=""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text(x_tolerance=1, y_tolerance=1) or ""
            text += "\n"
    return text

DISC_RE = re.compile(r"^\s*(\d)\s+([A-Za-zА-Яа-я0-9ёЁ/\-\.\(\) ,:+–—]+?)\s+(\d+)\s+(\d+)\s*$")

def chunk_by_disciplines(text):
    chunks=[]
    current_sem = None
    for line in text.splitlines():
        if "семестр" in line.lower():
            m = re.search(r"(\d)\s*семестр", line)
            if m:
                current_sem = int(m.group(1))
        m = DISC_RE.match(line)
        if m:
            sem, title, z, hours = m.groups()
            sem = int(sem)
            chunks.append({
                "semester": current_sem or sem,
                "title": title.strip(),
                "zachet": int(z),
                "hours": int(hours),
                "raw": line.strip()
            })
    return chunks

def build_docs(program_slug, text):
    # разбиваем по дисциплинам + избавляемся от дублей
    discs = chunk_by_disciplines(text)
    unique = {}
    for d in discs:
        key=(d["title"], d["semester"])
        if key not in unique:
            unique[key]=d
    docs=[]
    for (title, sem), d in unique.items():
        content = f"{title}. Семестр: {sem}. Трудоёмкость: {d['zachet']} з.е., {d['hours']} часов."
        docs.append({
            "id": str(uuid4()),
            "text": content,
            "meta": {
                "program": program_slug,
                "title": title,
                "semester": sem,
                "zachet": d["zachet"],
                "hours": d["hours"]
            }
        })
    return docs

def main():
    os.makedirs(PDF_DIR, exist_ok=True)
    pdfs = ensure_pdf()

    # загрузим модель эмбеддингов Qwen3-Embedding-0.6B
    model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")
    # рекомендуемые параметры (если хотите): flash_attention_2 и left padding — см. инструкции пользователя

    # инициализация Qdrant
    client = QdrantClient(QDRANT_URL)
    if COLLECTION not in [c.name for c in client.get_collections().collections]:
        client.recreate_collection(
            COLLECTION,
            vectors_config=VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE)
        )

    points=[]
    for path in pdfs:
        slug = "ai" if path.endswith("ai.pdf") else "ai_product"
        text = read_pdf_text(path)
        docs = build_docs(slug, text)
        embeddings = model.encode([d["text"] for d in docs], normalize_embeddings=True)
        for d, vec in zip(docs, embeddings):
            points.append(PointStruct(id=d["id"], vector=vec.tolist(), payload=d["meta"] | {"text": d["text"]}))
    if points:
        client.upsert(collection_name=COLLECTION, points=points)
        print(f"Upserted: {len(points)} points into {COLLECTION}")

if __name__ == "__main__":
    main()
