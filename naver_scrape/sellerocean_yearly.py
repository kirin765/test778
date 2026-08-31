"""Crawl sellerocean.com community boards, last-N-days window.

- Walks list pages (start=0,30,60,...) per board.
- Stops paging once all non-notice rows on a page are older than cutoff.
- Fetches detail pages with bounded concurrency.
- Appends each post to JSONL incrementally; skips bbs_num already in the file (resume).
"""
from __future__ import annotations
import argparse, json, re, sys, time, random, os, threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from scrapling.fetchers import Fetcher

BASE       = "https://sellerocean.com"
LIST_URL   = BASE + "/bbs_list.php?tb={tb}&start={start}"
DETAIL_URL = BASE + "/bbs_detail.php?bbs_num={num}&tb={tb}"
PAGE_STEP  = 30

# ---------- list page ----------

def parse_list(html: str, tb: str) -> list[tuple[str, str | None]]:
    """Return [(bbs_num, YYYY-MM-DD or None), ...] for non-notice rows of this board."""
    rows = []
    for tr in re.finditer(r"<tr\b[^>]*>(.+?)</tr>", html, flags=re.DOTALL):
        row = tr.group(1)
        m_num = re.search(rf"bbs_num=(\d+)[^\"']*?tb={re.escape(tb)}\b", row)
        if not m_num:
            continue  # notice rows link to tb=board_notice_all
        m_date = re.search(r'<span class="font_14"[^>]*>(\d{4}-\d{2}-\d{2})</span>', row)
        rows.append((m_num.group(1), m_date.group(1) if m_date else None))
    # dedupe preserving order
    seen, out = set(), []
    for n, d in rows:
        if n in seen: continue
        seen.add(n); out.append((n, d))
    return out

def list_until_cutoff(tb: str, cutoff: str, max_pages: int = 500,
                      sleep: float = 0.25) -> list[tuple[str, str]]:
    """Walk pages until cutoff or no new bbs_num appears (end of board reached)."""
    targets, start, empty_streak, no_new_streak = [], 0, 0, 0
    seen_nums: set[str] = set()
    for _ in range(max_pages):
        url = LIST_URL.format(tb=tb, start=start)
        try:
            p = Fetcher.get(url)
        except Exception as e:
            print(f"  [{tb}] list err start={start}: {e}", file=sys.stderr)
            break
        if p.status != 200:
            print(f"  [{tb}] list status={p.status} start={start}, stop")
            break
        rows = parse_list(p.body.decode("utf-8", "ignore"), tb)
        if not rows:
            empty_streak += 1
            if empty_streak >= 2: break
            start += PAGE_STEP; continue
        empty_streak = 0
        new_rows = [(n, d) for n, d in rows if n not in seen_nums]
        seen_nums.update(n for n, _ in new_rows)
        if not new_rows:
            no_new_streak += 1
            print(f"  [{tb}] start={start:5d} no new posts (streak {no_new_streak})")
            if no_new_streak >= 2: break
            start += PAGE_STEP; time.sleep(sleep); continue
        no_new_streak = 0
        in_window = [(n, d) for n, d in new_rows if d and d >= cutoff]
        last_date = next((d for _, d in reversed(new_rows) if d), None)
        targets.extend(in_window)
        print(f"  [{tb}] start={start:5d} rows={len(rows):2d} new={len(new_rows):2d} kept={len(in_window):2d} bottom={last_date}")
        if last_date and last_date < cutoff:
            break
        start += PAGE_STEP
        time.sleep(sleep)
    # dedupe
    seen, out = set(), []
    for n, d in targets:
        if n in seen: continue
        seen.add(n); out.append((n, d))
    return out

# ---------- detail page ----------

def parse_detail(html: str) -> dict:
    mt = re.search(r'<div class="detail_title">(.*?)</div>', html, flags=re.DOTALL)
    title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", mt.group(1))).strip() if mt else ""

    mc = re.search(r'<div class="detail_top_01[^"]*">(.*?)</div>', html, flags=re.DOTALL)
    category, date = "", ""
    if mc:
        parts = [x.strip() for x in re.sub(r"<[^>]+>", "|", mc.group(1)).split("|") if x.strip()]
        if parts: category = parts[0]
        m = re.search(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}", mc.group(1))
        if m: date = m.group(0)

    views = comments = recommends = 0
    mv = re.search(r"detail_top_02[^>]*>(.*?)</div>", html, flags=re.DOTALL)
    if mv:
        nums = re.findall(r"</i>\s*(\d+)", mv.group(1))
        if len(nums) >= 3:
            views, comments, recommends = int(nums[0]), int(nums[1]), int(nums[2])

    body = ""
    i = html.find("font_plus_minus")
    if i >= 0:
        end = html.find("</div>", i)
        if end >= 0:
            end2 = html.find("</div>", end + 6)
            i = (end2 if end2 >= 0 else end) + 6
    j = html.find("bbs_bottom_btn", i if i >= 0 else 0)
    if i >= 0 and j > i:
        chunk = html[i:j]
        chunk = re.sub(r"<script[^>]*>.*?</script>", "", chunk, flags=re.DOTALL)
        chunk = re.sub(r"<style[^>]*>.*?</style>",  "", chunk, flags=re.DOTALL)
        for marker in ["회원정보보기", "회원정보 닫기"]:
            k = chunk.find(marker)
            if k >= 0:
                chunk = chunk[:k]; break
        text = re.sub(r"<[^>]+>", " ", chunk).replace("&nbsp;", " ").replace("\xa0", " ")
        text = re.sub(r"\s+", " ", text).strip()
        body = re.sub(r"^내용\s*", "", text)

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

# ---------- main ----------

def load_done(path: str) -> set[tuple[str, str]]:
    done = set()
    if not os.path.exists(path): return done
    for line in open(path, "r", encoding="utf-8", errors="ignore"):
        try:
            r = json.loads(line)
            done.add((r["board"], str(r["bbs_num"])))
        except Exception:
            continue
    return done

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boards", default="board_generation_story,board_qna,sales,trouble")
    ap.add_argument("--days",   type=int, default=365, help="window size in days")
    ap.add_argument("--since",  default="", help="explicit cutoff YYYY-MM-DD (overrides --days)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--list-sleep", type=float, default=0.25)
    ap.add_argument("--detail-jitter", type=float, default=0.4)
    ap.add_argument("--out", default="posts_yearly.jsonl")
    args = ap.parse_args()

    cutoff = (args.since or
              (datetime.utcnow() - timedelta(days=args.days)).strftime("%Y-%m-%d"))
    boards = [b.strip() for b in args.boards.split(",") if b.strip()]
    print(f"[plan] cutoff={cutoff} boards={boards} workers={args.workers}")

    done = load_done(args.out)
    print(f"[resume] already in {args.out}: {len(done)} posts")

    targets: list[tuple[str, str]] = []  # (board, bbs_num)
    for tb in boards:
        rows = list_until_cutoff(tb, cutoff, sleep=args.list_sleep)
        new = [(tb, n) for n, _ in rows if (tb, n) not in done]
        print(f"[list] {tb}: {len(rows)} in window, {len(new)} new to fetch")
        targets.extend(new)

    print(f"[plan] total to fetch: {len(targets)}")
    if not targets:
        return

    out_lock = threading.Lock()
    ok = fail = 0
    f = open(args.out, "a", encoding="utf-8")

    def worker(tb, n):
        time.sleep(random.uniform(0, args.detail_jitter))
        return fetch_post(tb, n)

    try:
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures = [ex.submit(worker, tb, n) for tb, n in targets]
            for i, fut in enumerate(as_completed(futures), 1):
                rec = fut.result()
                if rec and rec.get("body"):
                    with out_lock:
                        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                        f.flush()
                    ok += 1
                else:
                    fail += 1
                if i % 25 == 0 or i == len(futures):
                    print(f"  [{i}/{len(futures)}] ok={ok} fail={fail}")
    finally:
        f.close()
    print(f"[done] appended {ok} posts to {args.out} (failed {fail})")

if __name__ == "__main__":
    main()
