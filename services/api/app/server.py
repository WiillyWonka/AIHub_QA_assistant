from fastapi import FastAPI
from .schema import AskRequest, AskResponse
from .llm import load_model, generate_answer
from .config import MODEL_QWEN, ALLOWED_PROGRAMM
from .plan_loader import load_plan

app = FastAPI(title="ITMO MAI RAG API")
tok, model = load_model(MODEL_QWEN)

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    if req.program not in ALLOWED_PROGRAMM:
        return AskResponse(answer="Я отвечаю только по программам «Искусственный интеллект» и «Управление ИИ‑продуктами». Уточните программу.", sources=[])

    learning_plan = load_plan(req.program)

    if learning_plan is None:
        return AskResponse(answer="Не удалось загрузить план по указанной программе. Попробуйте обратититься позже", sources=[])
    
    answer = generate_answer(tok, model, req.query, learning_plan, req.background)

    return AskResponse(answer=answer, sources=[])

@app.post("/recommend", response_model=AskResponse)
def recommend(req: AskRequest):
    
    prompt = f"Порекомендуй какие выборные дисциплины лучше прослушать абитуриенту в ходе обучения, с учетом бэкграунда абитуриента"
    learning_plan = load_plan(req.program)

    if learning_plan is None:
        return AskResponse(answer="Не удалось загрузить план по указанной программе. Попробуйте обратититься позже", sources=[])
    
    answer = generate_answer(tok, model, prompt, learning_plan, req.background)
    sources=[]
    return AskResponse(answer=answer, sources=sources)
