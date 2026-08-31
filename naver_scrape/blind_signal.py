"""Measure signal-word match rate per topic.

For each candidate topic URL, scroll the list page until N posts loaded,
extract title + preview text from each card, then compute the % of cards
whose title or preview contains any signal word.

Usage: python3 blind_signal.py
Output: signal_density.json + console table
"""
import asyncio, json, re, sys
from pathlib import Path
from playwright.async_api import async_playwright

CDP_URL = "http://localhost:9222"
N_PER_TOPIC = 50

# Candidate topics — user-suggested + workplace/work-tool adjacent
CANDIDATES = [
    ("회사생활", "https://www.teamblind.com/kr/topics/회사생활"),
    ("이직·커리어", "https://www.teamblind.com/kr/topics/이직·커리어"),
    ("기술사", "https://www.teamblind.com/kr/topics/기술사"),
    ("ChatGPT AI 활용", "https://www.teamblind.com/kr/topics/ChatGPT-AI-활용"),
]

# Mom Test signal words (skill spec)
SIGNAL_WORDS = [
    "불편", "문제", "아쉬운", "아쉽", "안 된다", "안돼", "안된다",
    "힘들다", "힘듦", "힘들어", "막막", "귀찮", "자동화",
    "대안", "없나요", "없을까", "방법없", "툴 추천", "툴추천",
    "노하우", "어떻게 하시나요", "노가다",
]
SIGNAL_RE = re.compile("|".join(re.escape(w) for w in SIGNAL_WORDS))


async def collect_cards(page, n):
    """Scroll list until at least n unique post cards collected. Return list of (url, title, preview)."""
    seen = {}
    last_count = 0
    stagnant = 0
    while len(seen) < n and stagnant < 4:
        cards = await page.evaluate("""
            () => {
                // Each card has an anchor to /kr/post/ + nearby text
                const out = [];
                document.querySelectorAll('a[href*="/kr/post/"]').forEach(a => {
                    // Climb to card container with full text
                    let p = a;
                    for (let i = 0; i < 5 && p; i++) {
                        if (p.innerText && p.innerText.length > 30) break;
                        p = p.parentElement;
                    }
                    const text = p ? p.innerText.trim() : (a.innerText || '');
                    out.push({ url: a.href, text: text.slice(0, 400) });
                });
                return out;
            }
        """)
        for c in cards:
            seen.setdefault(c["url"], c["text"])
        if len(seen) == last_count:
            stagnant += 1
        else:
            stagnant = 0
            last_count = len(seen)
        await page.evaluate("() => window.scrollBy(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1500)
    return [{"url": u, "text": t} for u, t in list(seen.items())[:n]]


async def probe_topic(ctx, name, url):
    page = await ctx.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        # Skip networkidle (Blind has continuous polling). Wait for first post link instead.
        try:
            await page.wait_for_selector('a[href*="/kr/post/"]', timeout=10000)
        except Exception:
            pass
        await page.wait_for_timeout(1500)
    except Exception as e:
        await page.close()
        return {"name": name, "url": url, "exists": False, "error": str(e)}

    # Check exists: does the page show post links?
    initial_count = await page.evaluate(
        "() => document.querySelectorAll('a[href*=\"/kr/post/\"]').length"
    )
    if initial_count == 0:
        # Maybe 404 / not-found page — check title
        page_title = await page.title()
        await page.close()
        return {"name": name, "url": url, "exists": False, "page_title": page_title}

    cards = await collect_cards(page, N_PER_TOPIC)
    matched = []
    for c in cards:
        m = SIGNAL_RE.search(c["text"])
        if m:
            matched.append({"url": c["url"], "preview": c["text"][:200], "hit": m.group(0)})
    await page.close()
    return {
        "name": name,
        "url": url,
        "exists": True,
        "collected": len(cards),
        "matched": len(matched),
        "match_rate": round(len(matched) / len(cards) * 100, 1) if cards else 0,
        "samples": matched[:5],
    }


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        ctx = browser.contexts[0]
        results = []
        for name, url in CANDIDATES:
            print(f"[probe] {name} → {url}", file=sys.stderr)
            r = await probe_topic(ctx, name, url)
            results.append(r)
            if r.get("exists"):
                print(
                    f"  collected={r['collected']} matched={r['matched']} ({r['match_rate']}%)",
                    file=sys.stderr,
                )
            else:
                print(f"  NOT FOUND: {r.get('page_title') or r.get('error')}", file=sys.stderr)
        out = Path(__file__).parent / "signal_density.json"
        out.write_text(json.dumps(results, ensure_ascii=False, indent=2))
        print("\n=== Signal density ===")
        print(f"{'Topic':<25} {'N':>4} {'Match':>6} {'%':>6}")
        for r in results:
            if r.get("exists"):
                print(f"{r['name']:<25} {r['collected']:>4} {r['matched']:>6} {r['match_rate']:>5}%")
            else:
                print(f"{r['name']:<25}  -- not found --")
        print(f"\nfull dump: {out}")


asyncio.run(main())
