"""PoC scraper for teamblind.com KR (refined selectors).

Connects to logged-in Chrome via CDP (port 9222), pulls N recent posts from
'채널 전체' list, then visits each to extract structured fields.

Output: posts_blind_poc.jsonl
Schema per record: url, post_id, channel, title, company, author, posted_at,
                   views, likes, comment_count, body, comments[]
"""
import asyncio, json, re, sys
from pathlib import Path
from urllib.parse import unquote

from playwright.async_api import async_playwright

CDP_URL = "http://localhost:9222"
LIST_URL = "https://www.teamblind.com/kr/topics/채널-전체"
OUT = Path(__file__).parent / "posts_blind_poc.jsonl"
N_POSTS = 8


def post_id(href: str) -> str:
    m = re.search(r"/kr/post/(.+?)(?:[?#]|$)", href)
    return unquote(m.group(1)) if m else ""


# Single JS extractor that returns all structured fields
EXTRACT_JS = r"""
() => {
    const txt = (el) => el ? el.innerText.trim() : '';
    const sel1 = (s, root=document) => root.querySelector(s);
    const selA = (s, root=document) => Array.from(root.querySelectorAll(s));

    // Header block
    const head = sel1('.article-view-head');
    const contents = sel1('.contents');

    // Title: H2 inside head
    const title = head ? txt(head.querySelector('h2')) : '';

    // Channel: H1 starting with "채널 "
    let channel = '';
    selA('h1').forEach(h => {
        const t = txt(h);
        if (t.startsWith('채널 ')) {
            channel = t.replace(/^채널\s+/, '').replace(/\s*·\s*(언팔로우|팔로우).*$/, '').trim();
        }
    });

    // Meta: company · author, 작성일, 조회수, 댓글, 좋아요
    let company = '', author = '', posted_at = '', views = '', likes = '', comment_count = '';
    if (head) {
        const headText = head.innerText;
        // pattern: "company\n·\nauthor\n작성일\n17분\n조회수\n145\n댓글\n11"
        const lines = headText.split('\n').map(s => s.trim()).filter(Boolean);
        const idxDot = lines.indexOf('·');
        if (idxDot > 0) {
            company = lines[idxDot - 1] || '';
            author = lines[idxDot + 1] || '';
        }
        const grab = (label) => {
            const i = lines.indexOf(label);
            return i >= 0 && i + 1 < lines.length ? lines[i + 1] : '';
        };
        posted_at = grab('작성일');
        views = grab('조회수');
        comment_count = grab('댓글');
    }

    // Body: p.contents-txt is the clean body container
    const bodyEl = sel1('p.contents-txt');
    const body = txt(bodyEl);

    // Tags: .tag-article (text starts with "tag ")
    const tags = selA('.tag-article').map(el => txt(el).replace(/^tag\s+/, '')).filter(Boolean);

    // Comments: div.wrap-comment.comment_area, exclude ads
    const comments = selA('div.wrap-comment.comment_area').map(el => {
        const lines = el.innerText.split('\n').map(s => s.trim()).filter(Boolean);
        // First line: company; second: '·'; third: author; rest: body + meta
        let c_company = '', c_author = '', c_body = '', c_posted = '', c_likes = '';
        const idxDot = lines.indexOf('·');
        if (idxDot > 0) {
            c_company = lines[idxDot - 1];
            c_author = lines[idxDot + 1];
        }
        // Body: lines after author/'작성자' marker, before '작성일'
        const idxPosted = lines.indexOf('작성일');
        let bodyStart = idxDot + 2;
        if (lines[bodyStart] === '작성자') bodyStart++;
        const bodyEnd = idxPosted >= 0 ? idxPosted : lines.length;
        c_body = lines.slice(bodyStart, bodyEnd).join('\n').trim();
        if (idxPosted >= 0 && idxPosted + 1 < lines.length) c_posted = lines[idxPosted + 1];
        return { company: c_company, author: c_author, body: c_body, posted_at: c_posted };
    }).filter(c => c.body && !/광고|Coupang|쿠팡/.test(c.body) && !/광고|Coupang/.test(c.author));

    return {
        title, channel, company, author, posted_at,
        views, comment_count,
        body, tags, comments
    };
}
"""


async def get_post_urls(page, n):
    await page.wait_for_load_state("networkidle", timeout=15000)
    hrefs = await page.evaluate("""
        () => Array.from(document.querySelectorAll('a[href*="/kr/post/"]'))
            .map(a => a.href)
    """)
    seen, out = set(), []
    for h in hrefs:
        pid = post_id(h)
        if not pid or pid in seen:
            continue
        seen.add(pid)
        out.append(h)
        if len(out) >= n:
            break
    return out


async def extract_post(page, url):
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    try:
        await page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        pass
    data = await page.evaluate(EXTRACT_JS)
    data["url"] = url
    data["post_id"] = post_id(url)
    return data


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        ctx = browser.contexts[0]
        page = next((pg for pg in ctx.pages if "teamblind.com/kr/topics" in pg.url), None)
        if page is None:
            page = await ctx.new_page()
            await page.goto(LIST_URL, wait_until="domcontentloaded")
        else:
            print(f"[reuse] {page.url}", file=sys.stderr)

        urls = await get_post_urls(page, N_POSTS)
        print(f"[collected] {len(urls)} post URLs", file=sys.stderr)

        detail = await ctx.new_page()
        OUT.write_text("")
        for i, url in enumerate(urls, 1):
            try:
                rec = await extract_post(detail, url)
                with OUT.open("a") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                print(
                    f"[{i}/{len(urls)}] [{rec['channel']}] {rec['title'][:30]}"
                    f" | {rec['company']}·{rec['author']}"
                    f" | body={len(rec['body'])} cmts={len(rec['comments'])}",
                    file=sys.stderr,
                )
            except Exception as e:
                print(f"[{i}/{len(urls)}] FAIL {url}: {e}", file=sys.stderr)
            await asyncio.sleep(1.0)
        await detail.close()
        print(f"\n[done] {OUT}")


asyncio.run(main())
