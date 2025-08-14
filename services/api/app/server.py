from fastapi import FastAPI
from .schema import AskRequest, AskResponse
from .rag import RAG
from .llm import load_model, generate_answer
from .config import MODEL_QWEN, MAX_CTX_CHARS

app = FastAPI(title="ITMO MAI RAG API")
rag = RAG()
tok, model = load_model(MODEL_QWEN)

ALLOWED = {"ai", "ai_product"}

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    if req.program not in ALLOWED:
        return AskResponse(answer="Я отвечаю только по программам «Искусственный интеллект» и «Управление ИИ‑продуктами». Уточните программу.", sources=[])

    ctx, hits = rag.retrieve(req.query, req.program)
    # ограничим размер контекста
    acc, total= [],0
    for c in ctx:
        if total + len(c) > MAX_CTX_CHARS: break
        acc.append(c); total += len(c)
    answer = generate_answer(tok, model, req.query, acc, req.background)

    sources=[]
    for h in hits:
        p=h.payload
        sources.append(f"{p['title']} (семестр {p['semester']}, {p['hours']} ч)")

    return AskResponse(answer=answer, sources=sources)

@app.post("/recommend", response_model=AskResponse)
def recommend(req: AskRequest):
    # переформулируем запрос в «рекомендации по элективам под бэкграунд»
    prompt = f"Порекомендуй 5-7 элективов из плана, учитывая бэкграунд: {req.background or 'не указан'}. Сформируй список: название — зачем и когда брать (семестр)."
    ctx, hits = rag.retrieve("список элективов и дисциплины по программе", req.program)
    answer = generate_answer(tok, model, prompt, ctx, req.background)
    sources=[f"{h.payload['title']} (семестр {h.payload['semester']})" for h in hits[:7]]
    return AskResponse(answer=answer, sources=sources)
