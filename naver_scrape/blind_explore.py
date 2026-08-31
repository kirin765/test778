"""PoC: connect via CDP, snapshot Blind KR topic list to find post link selectors."""
import asyncio, json, sys
from playwright.async_api import async_playwright

CDP_URL = "http://localhost:9222"
LIST_URL = "https://www.teamblind.com/kr/topics/채널-전체"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        ctx = browser.contexts[0]
        page = next((pg for pg in ctx.pages if "teamblind.com" in pg.url), None)
        if page is None:
            page = await ctx.new_page()
            await page.goto(LIST_URL, wait_until="domcontentloaded")
        else:
            print(f"reusing tab: {page.url}", file=sys.stderr)

        await page.wait_for_load_state("networkidle", timeout=15000)

        # Pull all anchor hrefs that look like post links + their text snippet
        links = await page.evaluate("""
            () => {
                const out = [];
                document.querySelectorAll('a[href]').forEach(a => {
                    const href = a.getAttribute('href') || '';
                    if (!href) return;
                    // Blind post URLs typically contain /topics/ or /post/ or article ids
                    out.push({
                        href: a.href,
                        text: (a.innerText || '').slice(0, 120).replace(/\\s+/g, ' ').trim()
                    });
                });
                return out;
            }
        """)

        # Also dump the body text snippet for orientation
        body_snippet = await page.evaluate("() => document.body.innerText.slice(0, 2000)")

        # Bucket all hrefs by path-prefix to learn URL shape
        from collections import Counter
        prefixes = Counter()
        for l in links:
            try:
                from urllib.parse import urlparse
                p = urlparse(l["href"])
                if p.netloc and "teamblind" in p.netloc:
                    parts = [x for x in p.path.split("/") if x][:3]
                    prefixes["/" + "/".join(parts)] += 1
            except Exception:
                pass

        print("=== href prefix counts ===")
        for k, v in prefixes.most_common(30):
            print(f"{v:4d}  {k}")

        # Sample 30 unique teamblind hrefs with text
        seen = set()
        print("\n=== sample teamblind links (30) ===")
        for l in links:
            if "teamblind.com" not in l["href"]:
                continue
            if l["href"] in seen:
                continue
            seen.add(l["href"])
            print(f"{l['href']}\n  ↳ {l['text']}\n")
            if len(seen) >= 30:
                break

        await browser.close()


asyncio.run(main())
