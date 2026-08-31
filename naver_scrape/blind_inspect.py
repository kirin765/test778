"""Inspect one post DOM to find precise selectors."""
import asyncio, sys, json
from playwright.async_api import async_playwright

URL = "https://www.teamblind.com/kr/post/%EC%9D%BD%EA%B3%A0-%ED%8C%A9%ED%8F%AD%EC%A2%80-t2s3i8jh"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        ctx = browser.contexts[0]
        page = await ctx.new_page()
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_load_state("networkidle", timeout=10000)

        # Dump all h-tags and their classes
        info = await page.evaluate("""
            () => {
                const out = { headings: [], articles: [], comments: [], post_block: null };

                // Walk up from title H2 ("읽고 팩폭좀") to find post container
                const titleH2 = Array.from(document.querySelectorAll('h2'))
                    .find(h => !h.innerText.includes('추천') && !h.innerText.includes('베스트'));
                if (titleH2) {
                    let p = titleH2.parentElement;
                    let walks = [];
                    for (let i = 0; i < 5 && p; i++) {
                        walks.push({
                            tag: p.tagName,
                            cls: p.className,
                            textLen: p.innerText.length,
                            snippet: p.innerText.slice(0, 300)
                        });
                        p = p.parentElement;
                    }
                    out.post_block = { titleH2_class: titleH2.className, parents: walks };
                }

                document.querySelectorAll('h1,h2,h3').forEach(el => {
                    out.headings.push({
                        tag: el.tagName,
                        cls: el.className,
                        text: el.innerText.slice(0, 80)
                    });
                });
                document.querySelectorAll('article').forEach(el => {
                    out.articles.push({
                        cls: el.className,
                        textLen: el.innerText.length,
                        snippet: el.innerText.slice(0, 200)
                    });
                });
                // Look for comment-ish containers
                document.querySelectorAll('[class*="comment" i], [class*="Comment"]').forEach(el => {
                    if (el.children.length > 0 || el.innerText.length > 10) {
                        out.comments.push({
                            tag: el.tagName,
                            cls: el.className,
                            kids: el.children.length,
                            snippet: el.innerText.slice(0, 150)
                        });
                    }
                });
                return out;
            }
        """)

        print(json.dumps(info, ensure_ascii=False, indent=2))
        await page.close()

asyncio.run(main())
