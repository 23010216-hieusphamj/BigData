"""Đo hiệu năng các truy vấn trong một file .sql: lưu EXPLAIN ANALYZE + thời gian chạy.

Ví dụ:
  python python/benchmark.py --label before
  python python/benchmark.py --label after --queries sql/queries/03_business_queries_optimized.sql
  python python/benchmark.py --label test --only Q1,Q2 --runs 2
"""
import argparse
import csv
import re
import statistics
import time
from datetime import datetime
from pathlib import Path

import mysql.connector
from config import DB_CONFIG

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SQL = ROOT / "sql" / "queries" / "02_business_queries_unoptimized.sql"
PLAN_DIR = ROOT / "results" / "plan"
TABLE_DIR = ROOT / "results" / "tables"

MARKER = re.compile(r"^--\s*@(Q\d+[A-Za-z]?)\s*\|\s*(.*)$")


def parse_queries(path):
    """Tách file .sql thành các truy vấn theo nhãn '-- @Qn | tiêu đề | ...'."""
    queries, cur = [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = MARKER.match(line.strip())
        if m:
            if cur:
                queries.append(cur)
            cur = {"id": m.group(1), "title": m.group(2).split("|")[0].strip(), "lines": []}
        elif cur is not None:
            cur["lines"].append(line)
    if cur:
        queries.append(cur)
    for q in queries:
        q["sql"] = "\n".join(q.pop("lines")).strip().rstrip(";").strip()
    return queries


def run_query(cur, sql):
    t = time.perf_counter()
    cur.execute(sql)
    rows = cur.fetchall()
    return time.perf_counter() - t, len(rows)


def explain_analyze(cur, sql):
    t = time.perf_counter()
    cur.execute("EXPLAIN ANALYZE " + sql)
    plan = cur.fetchall()[0][0]
    elapsed = time.perf_counter() - t
    if isinstance(plan, (bytes, bytearray)):
        plan = plan.decode("utf-8")
    return plan, elapsed


def write_csv(path, results):
    cols = ["query", "title", "rows_returned", "runs", "mean_s", "median_s",
            "stdev_s", "min_s", "max_s", "run_times_s"]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:   # utf-8-sig để Excel đọc đúng tiếng Việt
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(results)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--queries", default=str(DEFAULT_SQL), help="file .sql chứa các truy vấn")
    ap.add_argument("--label", default="before", help="nhãn kết quả: before / after / ...")
    ap.add_argument("--only", default="", help="chỉ chạy một số truy vấn, ví dụ Q1,Q3")
    ap.add_argument("--runs", type=int, default=5, help="số lần đo với truy vấn nhanh")
    ap.add_argument("--slow-runs", type=int, default=3, help="số lần đo với truy vấn chậm")
    ap.add_argument("--slow-threshold", type=float, default=30.0,
                    help="truy vấn có lần làm nóng lâu hơn số giây này được coi là chậm")
    ap.add_argument("--skip-explain", action="store_true", help="không chạy EXPLAIN ANALYZE")
    args = ap.parse_args()

    queries = parse_queries(Path(args.queries))
    if args.only:
        wanted = {x.strip().upper() for x in args.only.split(",")}
        queries = [q for q in queries if q["id"] in wanted]
    if not queries:
        raise SystemExit("Không tìm thấy truy vấn nào (kiểm tra nhãn '-- @Qn | ...').")

    PLAN_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    cfg = dict(DB_CONFIG)
    cfg.setdefault("charset", "utf8mb4")
    conn = mysql.connector.connect(**cfg)
    cur = conn.cursor()

    cur.execute("SELECT VERSION(), @@innodb_buffer_pool_size")
    version, bp = cur.fetchone()
    meta = (f"Thời điểm: {datetime.now():%Y-%m-%d %H:%M:%S}\n"
            f"MySQL: {version}\n"
            f"innodb_buffer_pool_size: {int(bp) // 1024 // 1024} MB\n"
            f"File truy vấn: {args.queries}\n"
            f"Nhãn: {args.label} | runs={args.runs}, slow_runs={args.slow_runs}, "
            f"slow_threshold={args.slow_threshold}s\n")
    (TABLE_DIR / f"meta_{args.label}.txt").write_text(meta, encoding="utf-8")
    print(meta, flush=True)

    out_csv = TABLE_DIR / f"benchmark_{args.label}.csv"
    results = []
    try:
        for q in queries:
            print(f"[{q['id']}] {q['title']}", flush=True)

            if args.skip_explain:
                warm, _ = run_query(cur, q["sql"])
                print(f"  Chạy làm nóng: {warm:.2f}s", flush=True)
            else:
                plan, warm = explain_analyze(cur, q["sql"])
                (PLAN_DIR / f"{q['id']}_explain_{args.label}.txt").write_text(
                    f"-- {q['id']} | {q['title']}\n-- nhãn: {args.label}\n\n{plan}\n",
                    encoding="utf-8")
                print(f"  EXPLAIN ANALYZE (làm nóng, đã lưu plan): {warm:.2f}s", flush=True)

            n_runs = args.slow_runs if warm > args.slow_threshold else args.runs
            times, n_rows = [], 0
            for i in range(n_runs):
                t, n_rows = run_query(cur, q["sql"])
                times.append(t)
                print(f"  Lần {i + 1}/{n_runs}: {t:.3f}s", flush=True)

            results.append({
                "query": q["id"], "title": q["title"], "rows_returned": n_rows, "runs": n_runs,
                "mean_s": round(statistics.mean(times), 4),
                "median_s": round(statistics.median(times), 4),
                "stdev_s": round(statistics.stdev(times), 4) if n_runs > 1 else 0,
                "min_s": round(min(times), 4), "max_s": round(max(times), 4),
                "run_times_s": ";".join(f"{x:.4f}" for x in times),
            })
            write_csv(out_csv, results)          # ghi sau mỗi truy vấn để không mất dữ liệu nếu dừng giữa chừng
    except KeyboardInterrupt:
        print("\nĐã dừng. Kết quả các truy vấn đã xong vẫn được lưu.")
    finally:
        cur.close()
        conn.close()

    print("\n=== TÓM TẮT ===")
    print(f"{'Query':<6}{'Số dòng':>10}{'Lần':>5}{'TB (s)':>10}{'Trung vị':>10}{'Độ lệch':>10}")
    for r in results:
        print(f"{r['query']:<6}{r['rows_returned']:>10}{r['runs']:>5}"
              f"{r['mean_s']:>10.3f}{r['median_s']:>10.3f}{r['stdev_s']:>10.3f}")
    print(f"\nĐã lưu: {out_csv}")


if __name__ == "__main__":
    main()