import asyncio, os, sys, re
from playwright.async_api import async_playwright

URL = sys.argv[1]
OUT_DIR = sys.argv[2]
NAME = sys.argv[3]  # "ai" | "ai_product"

BTN_TEXT = "Скачать учебный план"

async def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, f"{NAME}.pdf")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(accept_downloads=True)
        await page.goto(URL, wait_until="domcontentloaded")
        # клик по кнопке с видимым текстом
        btn = page.get_by_text(BTN_TEXT, exact=True)
        async with page.expect_download() as dl:
            await btn.click()
        download = await dl.value
        await download.save_as(out_path)
        await browser.close()
        print(out_path)

if __name__ == "__main__":
    asyncio.run(main())
