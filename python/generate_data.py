"""Sinh dữ liệu giả lập thương mại điện tử cho shop_db -> sql/data/*.csv"""
import time
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N_CUSTOMERS = 100_000
N_PRODUCTS = 10_000
N_ORDERS = 2_000_000

OUT = Path(__file__).resolve().parent.parent / "sql" / "data"
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(SEED)


def save(df, name):
    t = time.time()
    df.to_csv(OUT / f"{name}.csv", index=False, encoding="utf-8",
              lineterminator="\n", na_rep="\\N",
              date_format="%Y-%m-%d %H:%M:%S")
    print(f"  {name}.csv: {len(df):,} dòng ({time.time() - t:.1f}s)")


def random_datetimes(n, start, end):
    s, e = np.datetime64(start), np.datetime64(end)
    span = int((e - s).astype("timedelta64[s]").astype(np.int64))
    offsets = rng.integers(0, span, size=n)
    return pd.Series(s + offsets.astype("timedelta64[s]")).astype("datetime64[ns]")


t0 = time.time()

# ---------- categories ----------
cat_names = [
    "Điện thoại", "Laptop", "Máy tính bảng", "Phụ kiện", "Âm thanh",
    "Đồng hồ thông minh", "Máy ảnh", "Tivi", "Gia dụng", "Nhà bếp",
    "Thời trang nam", "Thời trang nữ", "Giày dép", "Túi xách", "Mỹ phẩm",
    "Sách", "Đồ chơi", "Thể thao", "Nội thất", "Thực phẩm",
]
n_cat = len(cat_names)
print("Đang sinh dữ liệu...")
save(pd.DataFrame({"category_id": range(1, n_cat + 1),
                   "category_name": cat_names}), "categories")

# ---------- customers ----------
ho = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ"]
dem = ["Văn", "Thị", "Minh", "Quốc", "Thanh", "Ngọc", "Hữu", "Đức"]
ten = ["An", "Bình", "Châu", "Dũng", "Giang", "Hà", "Hiếu", "Hoa", "Huy", "Khánh",
       "Lan", "Linh", "Minh", "Nam", "Phong", "Quân", "Sơn", "Thảo", "Trang", "Tuấn"]
cities = ["TP. Hồ Chí Minh", "Hà Nội", "Đà Nẵng", "Hải Phòng", "Cần Thơ",
          "Biên Hòa", "Nha Trang", "Huế", "Vũng Tàu", "Đà Lạt"]
city_p = [0.28, 0.24, 0.09, 0.07, 0.06, 0.06, 0.05, 0.05, 0.05, 0.05]

cid = np.arange(1, N_CUSTOMERS + 1)
domains = rng.choice(["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"],
                     size=N_CUSTOMERS, p=[0.6, 0.15, 0.15, 0.1])
phones = [f"09{x:08d}" for x in rng.integers(0, 10**8, N_CUSTOMERS)]
phone_null = rng.random(N_CUSTOMERS) < 0.05
customers = pd.DataFrame({
    "customer_id": cid,
    "full_name": [f"{a} {b} {c}" for a, b, c in
                  zip(rng.choice(ho, N_CUSTOMERS), rng.choice(dem, N_CUSTOMERS),
                      rng.choice(ten, N_CUSTOMERS))],
    "email": [f"user{i}@{d}" for i, d in zip(cid, domains)],
    "phone": pd.Series(phones).where(~phone_null),
    "city": rng.choice(cities, size=N_CUSTOMERS, p=city_p),
    "created_at": random_datetimes(N_CUSTOMERS, "2018-01-01T00:00:00", "2023-12-31T23:59:59"),
})
save(customers, "customers")

# ---------- products ----------
pid = np.arange(1, N_PRODUCTS + 1)
w = 1 / np.arange(1, n_cat + 1)          # danh mục phân bố lệch (Zipf)
w = w / w.sum()
category_id = rng.choice(np.arange(1, n_cat + 1), size=N_PRODUCTS, p=w)
prices = (np.round(np.exp(rng.normal(12.5, 0.8, N_PRODUCTS)) / 1000) * 1000)
prices = prices.clip(10_000, 50_000_000).astype(np.int64)
products = pd.DataFrame({
    "product_id": pid,
    "product_name": [f"{cat_names[c - 1]} mẫu {i}" for i, c in zip(pid, category_id)],
    "category_id": category_id,
    "price": prices,
    "stock": rng.integers(0, 1001, N_PRODUCTS),
    "created_at": random_datetimes(N_PRODUCTS, "2018-01-01T00:00:00", "2023-12-31T23:59:59"),
})
save(products, "products")

# ---------- order_items (sinh trước để tính total_amount) ----------
order_ids = np.arange(1, N_ORDERS + 1)
items_per_order = rng.choice([1, 2, 3, 4, 5], size=N_ORDERS, p=[0.20, 0.30, 0.25, 0.15, 0.10])
n_items = int(items_per_order.sum())
item_order_id = np.repeat(order_ids, items_per_order)
item_product_id = (N_PRODUCTS * rng.random(n_items) ** 2.5).astype(np.int64) + 1  # sản phẩm bán chạy lệch
quantity = rng.choice([1, 2, 3, 4, 5], size=n_items, p=[0.55, 0.25, 0.10, 0.06, 0.04])
unit_price = prices[item_product_id - 1]
order_items = pd.DataFrame({
    "order_item_id": np.arange(1, n_items + 1),
    "order_id": item_order_id,
    "product_id": item_product_id,
    "quantity": quantity,
    "unit_price": unit_price,
})
save(order_items, "order_items")

# ---------- orders ----------
totals = np.bincount(item_order_id, weights=quantity * unit_price,
                     minlength=N_ORDERS + 1)[1:].astype(np.int64)
order_dates = random_datetimes(N_ORDERS, "2020-01-01T00:00:00", "2025-12-31T23:59:59")
orders = pd.DataFrame({
    "order_id": order_ids,
    "customer_id": np.minimum(N_CUSTOMERS,
                              (rng.beta(0.8, 2.5, N_ORDERS) * N_CUSTOMERS).astype(np.int64) + 1),
    "order_date": order_dates.sort_values(ignore_index=True),   # order_id tăng theo thời gian
    "status": rng.choice(["completed", "shipped", "pending", "cancelled", "returned"],
                         size=N_ORDERS, p=[0.70, 0.10, 0.08, 0.07, 0.05]),
    "payment_method": rng.choice(["cod", "card", "bank_transfer", "e_wallet"],
                                 size=N_ORDERS, p=[0.40, 0.30, 0.20, 0.10]),
    "total_amount": totals,
})
save(orders, "orders")

print(f"Hoàn tất sau {time.time() - t0:.0f}s. File nằm trong: {OUT}")