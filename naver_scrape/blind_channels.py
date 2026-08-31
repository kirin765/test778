"""List all KR channels (name + URL) from the explore page."""
import asyncio, json
from playwright.async_api import async_playwright

URL = "https://www.teamblind.com/kr/channels/explore"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = await browser.contexts[0].new_page()
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_load_state("networkidle", timeout=15000)

        # Wait for any link to topics or channel cards
        await page.wait_for_timeout(3000)
        # Scroll to trigger lazy load
        await page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)
        await page.evaluate("() => window.scrollTo(0, 0)")
        body_snip = await page.evaluate("() => document.body.innerText.slice(0, 3000)")
        print("=== body snippet ===")
        print(body_snip)
        print("=== all anchors with href containing topics/ or channels/ ===")
        anchors = await page.evaluate("""
            () => Array.from(document.querySelectorAll('a[href]'))
                .filter(a => /\\/kr\\/(topics|channels)/.test(a.href))
                .map(a => ({ name: a.innerText.trim().slice(0,60), url: a.href }))
        """)
        seen = {}
        for c in anchors:
            seen.setdefault(c["url"], c["name"])
        print(f"\n=== {len(seen)} unique channel/topic links ===")
        for url, name in list(seen.items())[:200]:
            print(f"{name}\n  {url}")
        return
        seen = {}
        for c in channels:
            seen.setdefault(c["url"], c["name"])
        print(f"=== {len(seen)} unique channels ===")
        for url, name in seen.items():
            print(f"{name}\n  {url}")
        await page.close()

asyncio.run(main())
