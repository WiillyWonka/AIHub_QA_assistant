import os, asyncio, textwrap
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
import httpx

API_BASE = os.getenv("API_BASE", "http://api:8000")
TOKEN = os.getenv("TELEGRAM_TOKEN")

HELP = textwrap.dedent("""\
Привет! Я помогу сравнить 2 магистратуры ИТМО:
• «Искусственный интеллект» (ai)
• «Управление ИИ‑продуктами» (ai_product)

Команды:
- /ai текст_вопроса — спросить по программе ИИ
- /aip текст_вопроса — спросить по программе AI Product
- /rec_ai ваш_бэкграунд — подбор элективов (ИИ)
- /rec_aip ваш_бэкграунд — подбор элективов (AI Product)

Я отвечаю только по этим двум программам.
""")

dp = Dispatcher()

@dp.message(F.text.regexp(r"^/start|/help"))
async def help_msg(m: Message):
    await m.answer(HELP)

async def call_api(endpoint: str, program: str, query: str, background: str|None=None):
    async with httpx.AsyncClient(timeout=60) as cx:
        payload={"query":query, "program":program, "background": background}
        r = await cx.post(f"{API_BASE}{endpoint}", json=payload)
        r.raise_for_status()
        return r.json()

@dp.message(F.text.regexp(r"^/ai\s+(.+)$"))
async def ask_ai(m: Message, regexp_dict):
    q = regexp_dict.group(1)
    res = await call_api("/ask","ai",q)
    await m.answer(res["answer"])

@dp.message(F.text.regexp(r"^/aip\s+(.+)$"))
async def ask_aip(m: Message, regexp_dict):
    q = regexp_dict.group(1)
    res = await call_api("/ask","ai_product",q)
    await m.answer(res["answer"])

@dp.message(F.text.regexp(r"^/rec_ai\s+(.+)$"))
async def rec_ai(m: Message, regexp_dict):
    bg = regexp_dict.group(1)
    res = await call_api("/recommend","ai","Рекомендации по элективам", bg)
    await m.answer(res["answer"])

@dp.message(F.text.regexp(r"^/rec_aip\s+(.+)$"))
async def rec_aip(m: Message, regexp_dict):
    bg = regexp_dict.group(1)
    res = await call_api("/recommend","ai_product","Рекомендации по элективам", bg)
    await m.answer(res["answer"])

@dp.message()
async def fallback(m: Message):
    await m.answer("Я отвечаю только по программам «Искусственный интеллект» и «Управление ИИ‑продуктами». Наберите /help")

def main():
    bot = Bot(token=TOKEN)
    dp.run_polling(bot)

if __name__ == "__main__":
    main()
