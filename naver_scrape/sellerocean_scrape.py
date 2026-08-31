"""Bulk-collect community posts text from sellerocean.com.

Usage:
  python sellerocean_scrape.py --boards board_guin,board_qna --pages 5 --out posts.jsonl
"""
from __future__ import annotations
import argparse, json, re, sys, time, random
from concurrent.futures import ThreadPoolExecutor, as_completed
from scrapling.fetchers import Fetcher

BASE = "https://sellerocean.com"

DEFAULT_BOARDS = [
    "board_guin",              # 구인구직
    "board_qna",               # Q&A
    "board_generation_story",  # 세대 이야기
    "board_bestseller",        # 베스트셀러
    "board_faq",               # FAQ
]

LIST_URL   = BASE + "/bbs_list.php?tb={tb}&start={start}"
DETAIL_URL = BASE + "/bbs_detail.php?bbs_num={num}&tb={tb}"

def list_post_nums(tb: str, start: int) -> list[str]:
    p = Fetcher.get(LIST_URL.format(tb=tb, start=start))
    if p.status != 200:
        return []
    html = p.body.decode("utf-8", "ignore")
    # bbs_num=NN&...&tb=<tb>  (only links that target this same board)
    nums = re.findall(rf'bbs_num=(\d+)[^"\']*?tb={re.escape(tb)}', html)
    return list(dict.fromkeys(nums))  # dedupe, keep order

def parse_detail(html: str) -> dict:
    # title
    mt = re.search(r'<div class="detail_title">(.*?)</div>', html, flags=re.DOTALL)
    title = re.sub(r"<[^>]+>", " ", mt.group(1)).strip() if mt else ""
    title = re.sub(r"\s+", " ", title)

    # category + date in .detail_top_01
    mc = re.search(r'<div class="detail_top_01[^"]*">(.*?)</div>', html, flags=re.DOTALL)
    category, date = "", ""
    if mc:
        raw = re.sub(r"<[^>]+>", "|", mc.group(1))
        parts = [p.strip() for p in raw.split("|") if p.strip()]
        if parts:
            category = parts[0]
        m_date = re.search(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}", mc.group(1))
        if m_date:
            date = m_date.group(0)

    # views / comments / recommends
    mv = re.search(r'detail_top_02[^>]*>(.*?)</div>', html, flags=re.DOTALL)
    views = comments = recommends = 0
    if mv:
        nums = re.findall(r"</i>\s*(\d+)", mv.group(1))
        if len(nums) >= 3:
            views, comments, recommends = int(nums[0]), int(nums[1]), int(nums[2])

    # body: starts after the font-resize button block, ends before bbs_bottom_btn
    i = html.find("font_plus_minus")
    if i >= 0:
        # advance past the closing </div> of that header block (2 levels)
        end = html.find("</div>", i)
        if end >= 0:
            end2 = html.find("</div>", end + 6)
            i = (end2 if end2 >= 0 else end) + 6
    j = html.find("bbs_bottom_btn", i if i >= 0 else 0)
    # also try to cut at the member-info block which marks end of body
    body = ""
    if i >= 0 and j > i:
        chunk = html[i:j]
        chunk = re.sub(r"<script[^>]*>.*?</script>", "", chunk, flags=re.DOTALL)
        chunk = re.sub(r"<style[^>]*>.*?</style>",  "", chunk, flags=re.DOTALL)
        # cut at member-info popup / scrap line which always trails the body
        for marker in ["회원정보보기", "회원정보 닫기"]:
            k = chunk.find(marker)
            if k >= 0:
                chunk = chunk[:k]
                break
        text = re.sub(r"<[^>]+>", " ", chunk)
        text = text.replace("&nbsp;", " ").replace("\xa0", " ")
        text = re.sub(r"\s+", " ", text).strip()
        # drop a leading "내용" label (BBS template)
        text = re.sub(r"^내용\s*", "", text)
        body = text

    return {"title": title, "category": category, "date": date,
            "views": views, "comments": comments, "recommends": recommends,
            "body": body}

def fetch_post(tb: str, num: str, retries: int = 2) -> dict | None:
    url = DETAIL_URL.format(num=num, tb=tb)
    for attempt in range(retries + 1):
        try:
            p = Fetcher.get(url)
            if p.status == 200:
                rec = parse_detail(p.body.decode("utf-8", "ignore"))
                rec["url"] = url; rec["board"] = tb; rec["bbs_num"] = num
                return rec
        except Exception as e:
            if attempt == retries:
                print(f"  ERR {url}: {e}", file=sys.stderr)
        time.sleep(0.6 * (attempt + 1))
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boards", default=",".join(DEFAULT_BOARDS),
                    help="comma-separated board ids (e.g. board_guin,board_qna)")
    ap.add_argument("--pages", type=int, default=2,
                    help="how many list pages per board (each page ~28 posts)")
    ap.add_argument("--limit", type=int, default=0,
                    help="overall post cap (0 = no cap)")
    ap.add_argument("--workers", type=int, default=4,
                    help="concurrent detail fetchers")
    ap.add_argument("--delay", type=float, default=0.4,
                    help="sleep between detail fetches per worker (sec)")
    ap.add_argument("--out", default="posts.jsonl")
    args = ap.parse_args()

    boards = [b.strip() for b in args.boards.split(",") if b.strip()]
    print(f"[plan] boards={boards} pages={args.pages} workers={args.workers}")

    targets: list[tuple[str, str]] = []
    for tb in boards:
        for page_idx in range(args.pages):
            start = page_idx * 30
            nums = list_post_nums(tb, start)
            print(f"  list {tb} start={start} -> {len(nums)} posts")
            for n in nums:
                targets.append((tb, n))
            time.sleep(0.3)
    # de-dup
    seen = set(); uniq = []
    for tb, n in targets:
        k = (tb, n)
        if k in seen: continue
        seen.add(k); uniq.append(k)
    if args.limit and len(uniq) > args.limit:
        uniq = uniq[:args.limit]
    print(f"[plan] unique posts to fetch: {len(uniq)}")

    ok = 0; fail = 0
    with open(args.out, "w", encoding="utf-8") as f, \
         ThreadPoolExecutor(max_workers=args.workers) as ex:
        def worker(tb, n):
            time.sleep(random.uniform(0, args.delay))
            return fetch_post(tb, n)
        futures = [ex.submit(worker, tb, n) for tb, n in uniq]
        for i, fut in enumerate(as_completed(futures), 1):
            rec = fut.result()
            if rec and rec.get("body"):
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                ok += 1
            else:
                fail += 1
            if i % 10 == 0 or i == len(futures):
                print(f"  [{i}/{len(futures)}] ok={ok} fail={fail}")
    print(f"[done] saved {ok} posts to {args.out} (failed {fail})")

if __name__ == "__main__":
    main()
