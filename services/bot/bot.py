import os, asyncio, textwrap, re
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
import httpx

API_BASE = os.getenv("API_BASE", "http://api:8000")
TOKEN = os.getenv("TELEGRAM_TOKEN")

HELP = textwrap.dedent(
    """\ Привет! Я помогу сравнить 2 магистратуры ИТМО: • «Искусственный интеллект» (ai) • «Управление ИИ‑продуктами» (ai_product) Команды: - /ai текст_вопроса — спросить по программе ИИ - /aip текст_вопроса — спросить по программе AI Product - /rec_ai ваш_бэкграунд — подбор элективов (ИИ) - /rec_aip ваш_бэкграунд — подбор элективов (AI Product) Я отвечаю только по этим двум программам. """
)

dp = Dispatcher()


@dp.message(F.text.regexp(r"^/(start|help)$"))
async def help_msg(m: Message):
    await m.answer(HELP)


async def call_api(
    endpoint: str, program: str, query: str, background: str | None = None
):
    async with httpx.AsyncClient(timeout=60) as cx:
        r = await cx.post(
            f"{API_BASE}{endpoint}",
            json={"query": query, "program": program, "background": background},
        )
        r.raise_for_status()
        return r.json()


# 👇 даём имя результату регэкса через .as_("rx")
@dp.message(F.text.regexp(r"^/ai\s+(.+)$").as_("rx"))
async def ask_ai(m: Message, rx: re.Match):
    q = rx.group(1)
    res = await call_api("/ask", "ai", q)
    await m.answer(res["answer"])


@dp.message(F.text.regexp(r"^/aip\s+(.+)$").as_("rx"))
async def ask_aip(m: Message, rx: re.Match):
    q = rx.group(1)
    res = await call_api("/ask", "ai_product", q)
    await m.answer(res["answer"])


@dp.message(F.text.regexp(r"^/rec_ai\s+(.+)$").as_("rx"))
async def rec_ai(m: Message, rx: re.Match):
    bg = rx.group(1)
    res = await call_api("/recommend", "ai", "Рекомендации по элективам", bg)
    await m.answer(res["answer"])


@dp.message(F.text.regexp(r"^/rec_aip\s+(.+)$").as_("rx"))
async def rec_aip(m: Message, rx: re.Match):
    bg = rx.group(1)
    res = await call_api("/recommend", "ai_product", "Рекомендации по элективам", bg)
    await m.answer(res["answer"])


@dp.message()
async def fallback(m: Message):
    await m.answer(
        "Я отвечаю только по программам «Искусственный интеллект» и «Управление ИИ-продуктами». Наберите /help"
    )


async def main():
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
