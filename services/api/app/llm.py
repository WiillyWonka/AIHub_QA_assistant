from transformers import AutoTokenizer, AutoModelForCausalLM
import torch, textwrap

SYS = """Ты — помощник-навигатор для абитуриента. Отвечай ТОЛЬКО по двум программам ИТМО:
1) «Искусственный интеллект» (AI),
2) «Управление ИИ-продуктами / AI Product».
Если вопрос не про них — вежливо откажись и предложи обсудить только эти программы.

Инструкции:
- Используй предоставленный контекст (RAG). Если ответа нет в контексте — скажи, что в учебных планах нет прямого ответа (предложи связаться с менеджером программы со страницы), не выдумывай.
- Отвечай кратко и структурировано. Русский язык.
- При рекомендациях по элективам учитывай бэкграунд, но предлагай из списков этих программ.
"""

def load_model(model_name: str):
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto"
    )
    return tok, model

def generate_answer(tok, model, question: str, ctx: list[str], background: str | None):
    ctx_text = "\n".join(ctx) if ctx else "Нет релевантных фрагментов."
    bkg = f"Бэкграунд абитуриента: {background}" if background else ""
    user = textwrap.dedent(f"""
    Вопрос: {question}
    {bkg}
    Контекст:
    {ctx_text}
    """).strip()

    messages = [{"role": "system", "content": SYS}, {"role":"user","content": user}]
    text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=True)
    inputs = tok([text], return_tensors="pt").to(model.device)
    gen = model.generate(**inputs, max_new_tokens=800)
    out_ids = gen[0][len(inputs.input_ids[0]):].tolist()
    # отделим hidden thinking, если есть
    try:
        idx = len(out_ids) - out_ids[::-1].index(151668)  # </think>
    except ValueError:
        idx = 0
    content = tok.decode(out_ids[idx:], skip_special_tokens=True).strip()
    return content
