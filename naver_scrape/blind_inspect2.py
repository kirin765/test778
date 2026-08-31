"""Find precise body-only container by enumerating .contents children."""
import asyncio, json
from playwright.async_api import async_playwright

URL = "https://www.teamblind.com/kr/post/%EA%B8%88%EB%B3%B4%EC%9B%90-kj0040uu"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = await browser.contexts[0].new_page()
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_load_state("networkidle", timeout=10000)
        info = await page.evaluate("""
            () => {
                const c = document.querySelector('.article-view-contents');
                if (!c) return null;
                return Array.from(c.children).map(el => ({
                    tag: el.tagName,
                    cls: el.className,
                    textLen: el.innerText.length,
                    snippet: el.innerText.slice(0, 200)
                }));
            }
        """)
        print(json.dumps(info, ensure_ascii=False, indent=2))
        await page.close()

asyncio.run(main())
