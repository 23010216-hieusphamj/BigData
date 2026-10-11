"""Gộp các file benchmark thành bảng so sánh và biểu đồ cho báo cáo và slide.

Chạy từ thư mục gốc dự án:  python python/make_report_tables.py
Đầu vào : results/tables/benchmark_<nhãn>.csv
Đầu ra  : results/tables/so_sanh_truoc_sau.csv và .md
          results/tables/tien_trinh_tung_buoc.csv
          results/charts/*.png
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "results" / "tables"
CHARTS = ROOT / "results" / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

_cache = {}


def load(label):
    if label not in _cache:
        p = TABLES / f"benchmark_{label}.csv"
        _cache[label] = pd.read_csv(p, encoding="utf-8-sig").set_index("query") if p.exists() else None
    return _cache[label]


def get(label, qid):
    df = load(label)
    if df is None or qid not in df.index:
        return None
    r = df.loc[qid]
    return {"mean": float(r["mean_s"]), "median": float(r["median_s"]),
            "stdev": float(r["stdev_s"]), "runs": int(r["runs"])}


# ---------------------------------------------------------------------------
# 1. Bảng so sánh baseline và kết quả cuối cùng
#    (mã, mô tả, kỹ thuật, mã truy vấn trong file baseline, nhãn file cuối, mã truy vấn trong file cuối)
# ---------------------------------------------------------------------------
SUMMARY = [
    ("Q1", "Đơn hoàn tất trong tháng", "Covering index (status, order_date, ...)", "Q1", "final_core", "Q1"),
    ("Q2", "Doanh thu tháng 3/2025", "Bỏ hàm bọc cột + covering index", "Q2", "final_core", "Q2"),
    ("Q3", "Tìm khách theo email và đơn", "Index email + index theo customer_id", "Q3", "final_core", "Q3"),
    ("Q4", "Doanh thu theo tháng, danh mục", "Covering index (chỉ dùng index)", "Q4", "final_core", "Q4"),
    ("Q4S", "Doanh thu theo tháng, danh mục", "Bảng tổng hợp", "Q4", "final_summary", "Q4S"),
    ("Q5", "Top 3 sản phẩm mỗi danh mục", "Gom nhóm trước + covering index", "Q5", "final_core", "Q5"),
    ("Q5S", "Top 3 sản phẩm mỗi danh mục", "Bảng tổng hợp", "Q5", "final_summary", "Q5S"),
    ("Q6A", "Giá cao hơn trung bình danh mục", "Viết lại bằng JOIN", "Q6", "final_core", "Q6A"),
    ("Q6B", "Giá cao hơn trung bình danh mục", "Viết lại bằng window function", "Q6", "final_core", "Q6B"),
    ("Q7A", "Phân trang sâu", "Keyset + FORCE INDEX", "Q7", "final_q7a_fix", "Q7A"),
    ("Q7B", "Phân trang sâu", "Deferred join", "Q7", "final_core", "Q7B"),
    ("Q8", "Top 10 khách ở Hà Nội", "Composite + covering index", "Q8", "final_core", "Q8"),
    ("Q8S", "Top 10 khách ở Hà Nội", "Bảng tổng hợp", "Q8", "final_summary", "Q8S"),
]

# ---------------------------------------------------------------------------
# 2. Tiến trình từng bước của mỗi truy vấn (tên mốc, nhãn file, mã truy vấn)
# ---------------------------------------------------------------------------
TIMELINE = {
    "Q1": [("Baseline", "before", "Q1"), ("Index đơn", "step1_index", "Q1"),
           ("Covering", "step3a_orders_idx", "Q1"), ("Đo cuối", "final_core", "Q1")],
    "Q2": [("Baseline", "before", "Q2"), ("Index đơn", "step1_index", "Q2"),
           ("Viết lại", "step2_rewrite", "Q2"), ("Covering", "step3a_orders_idx", "Q2"),
           ("Đo cuối", "final_core", "Q2")],
    "Q3": [("Baseline", "before", "Q3"), ("Index đơn", "step1_index", "Q3"),
           ("Covering", "step3c_q8", "Q3"), ("Đo cuối", "final_core", "Q3")],
    "Q4": [("Baseline", "before", "Q4"), ("Index đơn", "step1_q4q8", "Q4"),
           ("Covering", "step3b_items_idx", "Q4"), ("Đo cuối", "final_core", "Q4"),
           ("Bảng tổng hợp", "final_summary", "Q4S")],
    "Q5": [("Baseline", "before", "Q5"), ("Viết lại", "step2_rewrite", "Q5"),
           ("Covering", "step3b_items_idx", "Q5"), ("Đo cuối", "final_core", "Q5"),
           ("Bảng tổng hợp", "final_summary", "Q5S")],
    "Q6": [("Baseline", "before", "Q6"), ("Viết lại JOIN", "step2_rewrite", "Q6A"),
           ("Đo cuối", "final_core", "Q6A")],
    "Q7": [("Baseline", "before", "Q7"), ("Index đơn", "step1_index", "Q7"),
           ("Keyset", "step2_rewrite", "Q7A"), ("Đo cuối (lỗi)", "final_core", "Q7A"),
           ("Sửa FORCE INDEX", "final_q7a_fix", "Q7A")],
    "Q8": [("Baseline", "before", "Q8"), ("Index đơn", "step1_q4q8", "Q8"),
           ("Covering", "step3c_q8", "Q8"), ("Đo cuối", "final_core", "Q8"),
           ("Bảng tổng hợp", "final_summary", "Q8S")],
}


def vn(text):
    """Đổi dấu số kiểu Anh (1,234.5) sang kiểu Việt (1.234,5)."""
    return text.replace(",", "\0").replace(".", ",").replace("\0", ".")


def fmt_s(x):
    if x >= 10:
        return vn(f"{x:,.2f}")
    if x >= 1:
        return vn(f"{x:,.3f}")
    return vn(f"{x:,.4f}")


def fmt_x(x):
    return vn(f"{x:,.1f}") if x < 10 else vn(f"{x:,.0f}")


def build_summary():
    rows = []
    for code, desc, tech, base_q, final_label, final_q in SUMMARY:
        b, f = get("before", base_q), get(final_label, final_q)
        if b is None or f is None:
            print(f"  (bỏ qua {code}: thiếu dữ liệu)")
            continue
        rows.append({
            "Truy vấn": code, "Mô tả": desc, "Kỹ thuật": tech,
            "Baseline TB (s)": b["mean"], "Baseline lệch chuẩn (s)": b["stdev"],
            "Cuối TB (s)": f["mean"], "Cuối lệch chuẩn (s)": f["stdev"],
            "Tăng tốc (TB)": b["mean"] / f["mean"],
            "Tăng tốc (trung vị)": b["median"] / f["median"],
        })
    return pd.DataFrame(rows)


def write_markdown(df, path):
    head = ["Truy vấn", "Kỹ thuật", "Baseline (s)", "Cuối (s)", "Tăng tốc (TB)", "Tăng tốc (trung vị)"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join([
            r["Truy vấn"], r["Kỹ thuật"],
            f"{fmt_s(r['Baseline TB (s)'])} ± {fmt_s(r['Baseline lệch chuẩn (s)'])}",
            f"{fmt_s(r['Cuối TB (s)'])} ± {fmt_s(r['Cuối lệch chuẩn (s)'])}",
            fmt_x(r["Tăng tốc (TB)"]) + " lần", fmt_x(r["Tăng tốc (trung vị)"]) + " lần"]) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_timeline():
    rows = []
    for q, stages in TIMELINE.items():
        for i, (stage, label, qid) in enumerate(stages):
            m = get(label, qid)
            if m:
                rows.append({"Truy vấn": q, "Thứ tự": i, "Mốc": stage, "File": label, "Mã trong file": qid,
                             "TB (s)": m["mean"], "Trung vị (s)": m["median"], "Lệch chuẩn (s)": m["stdev"]})
    return pd.DataFrame(rows)


def chart_before_after(df):
    fig, ax = plt.subplots(figsize=(13, 5.8))
    x = list(range(len(df)))
    w = 0.38
    ax.bar([i - w / 2 for i in x], df["Baseline TB (s)"], w, label="Baseline (chưa tối ưu)", color="#9aa0a6")
    ax.bar([i + w / 2 for i in x], df["Cuối TB (s)"], w, label="Sau tối ưu", color="#1a73e8")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(df["Truy vấn"])
    ax.set_ylabel("Thời gian trung bình (giây, thang log)")
    ax.set_title("Thời gian truy vấn trước và sau tối ưu")
    for i, (f, s) in enumerate(zip(df["Cuối TB (s)"], df["Tăng tốc (TB)"])):
        ax.text(i + w / 2, f * 1.25, "x" + fmt_x(s), ha="center", fontsize=8)
    ax.grid(axis="y", alpha=0.3, which="both")
    ax.legend()
    fig.tight_layout()
    fig.savefig(CHARTS / "truoc_sau_toi_uu.png", dpi=160)
    plt.close(fig)


def chart_timeline(tl):
    fig, axes = plt.subplots(2, 4, figsize=(19, 8.5))
    for ax, q in zip(axes.flat, TIMELINE):
        d = tl[tl["Truy vấn"] == q].sort_values("Thứ tự")
        xs = list(range(len(d)))
        ax.plot(xs, d["TB (s)"], marker="o", color="#1a73e8")
        for xi, (_, r) in zip(xs, d.iterrows()):
            ax.annotate(fmt_s(r["TB (s)"]), (xi, r["TB (s)"]), textcoords="offset points",
                        xytext=(0, 7), ha="center", fontsize=8)
        ax.set_yscale("log")
        ax.set_xticks(xs)
        ax.set_xticklabels(d["Mốc"], rotation=25, ha="right", fontsize=8)
        ax.set_title(q)
        ax.set_ylabel("giây (thang log)")
        ax.margins(y=0.35)
        ax.grid(alpha=0.3, which="both")
    fig.suptitle("Tiến trình tối ưu từng truy vấn qua các bước", fontsize=14)
    fig.tight_layout()
    fig.savefig(CHARTS / "tien_trinh_tung_buoc.png", dpi=160)
    plt.close(fig)


def chart_tradeoff():
    """Số liệu lấy từ results/tables/chi_phi_ghi.md và các bảng dung lượng (sửa tay nếu số của bạn khác)."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.5, 4.8))
    names = ["INSERT 500k đơn", "INSERT 500k\ndòng chi tiết", "UPDATE 100k đơn"]
    no_idx = [24.875, 25.696, 4.453]
    with_idx = [57.672, 51.929, 13.812]
    x = list(range(3))
    w = 0.38
    a1.bar([i - w / 2 for i in x], no_idx, w, label="Không index phụ", color="#9aa0a6")
    a1.bar([i + w / 2 for i in x], with_idx, w, label="Có index (bước 3)", color="#ea4335")
    for i, (a, b) in enumerate(zip(no_idx, with_idx)):
        a1.text(i + w / 2, b + 1, f"x{vn(f'{b / a:.1f}')}", ha="center", fontsize=9)
    a1.set_xticks(x)
    a1.set_xticklabels(names)
    a1.set_ylabel("giây")
    a1.set_title("Chi phí ghi khi có thêm index")
    a1.legend()
    steps = ["Baseline", "Sau bước 1\n(index đơn)", "Sau bước 3\n(covering)"]
    index_mb = [0, 66.6, 444.3]
    a2.bar(steps, index_mb, color="#fbbc04")
    a2.axhline(327.3, ls="--", color="#333", label="Tổng dữ liệu (327,3 MB)")
    for i, v in enumerate(index_mb):
        a2.text(i, v + 8, vn(f"{v:.1f}") + " MB", ha="center", fontsize=9)
    a2.set_ylabel("MB")
    a2.set_title("Dung lượng index qua các bước")
    a2.legend()
    fig.tight_layout()
    fig.savefig(CHARTS / "chi_phi_danh_doi.png", dpi=160)
    plt.close(fig)


def main():
    df = build_summary()
    df.to_csv(TABLES / "so_sanh_truoc_sau.csv", index=False, encoding="utf-8-sig")
    write_markdown(df, TABLES / "so_sanh_truoc_sau.md")
    tl = build_timeline()
    tl.to_csv(TABLES / "tien_trinh_tung_buoc.csv", index=False, encoding="utf-8-sig")
    chart_before_after(df)
    chart_timeline(tl)
    chart_tradeoff()
    print((TABLES / "so_sanh_truoc_sau.md").read_text(encoding="utf-8"))
    print("Đã tạo:")
    for p in ["results/tables/so_sanh_truoc_sau.csv", "results/tables/so_sanh_truoc_sau.md",
              "results/tables/tien_trinh_tung_buoc.csv", "results/charts/truoc_sau_toi_uu.png",
              "results/charts/tien_trinh_tung_buoc.png", "results/charts/chi_phi_danh_doi.png"]:
        print("  ", p)


if __name__ == "__main__":
    main()