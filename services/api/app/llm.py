from transformers import AutoTokenizer, AutoModelForCausalLM
import torch, textwrap

SYS = """Ты — помощник-навигатор для абитуриента. Отвечай ТОЛЬКО по двум программам ИТМО:
1) «Искусственный интеллект» (AI),
2) «Управление ИИ-продуктами / AI Product».
Если вопрос не про них — вежливо откажись и предложи обсудить только эти программы.

Инструкции:
- Используй предоставленный контекст. Если ответа нет в контексте — скажи, что в учебных планах нет прямого ответа (предложи связаться с менеджером программы со страницы), не выдумывай.
- Отвечай кратко и структурировано. Всё общение ведётся на русском языке.
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

def generate_answer(tokenizer, model, question: str, ctx: str, background: str | None = None):
    bkg = f"Бэкграунд абитуриента: {background}" if background else ""
    messages = [
        {"role": "system", "content": SYS},
        {"role": "user", "content": textwrap.dedent(f"""
        Вопрос: {question}
        {bkg}
        Контекст:
        {ctx}
        """).strip()}
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    # conduct text completion
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=32768
    )
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 
    # parsing thinking content
    try:
        # rindex finding 151668 (</think>)
        index = len(output_ids) - output_ids[::-1].index(151668)
    except ValueError:
        index = 0

    thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
    content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

    return content