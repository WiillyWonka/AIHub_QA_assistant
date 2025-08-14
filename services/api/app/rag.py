from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, SearchRequest
from sentence_transformers import SentenceTransformer
from .config import QDRANT_URL, COLLECTION, TOP_K

class RAG:
    def __init__(self):
        self.qdrant = QdrantClient(QDRANT_URL)
        self.emb = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")

    def retrieve(self, query: str, program: str):
        qvec = self.emb.encode([query], prompt_name="query", normalize_embeddings=True)[0].tolist()
        flt = Filter(must=[FieldCondition(key="program", match=MatchValue(value=program))])
        hits = self.qdrant.search(
            collection_name=COLLECTION,
            query_vector=qvec,
            query_filter=flt,
            limit=TOP_K
        )
        ctx=[]
        for h in hits:
            p=h.payload
            ctx.append(f"- {p['title']} (семестр {p['semester']}, {p['hours']} ч): {p['text']}")
        return ctx, hits
