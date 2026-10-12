"""Nạp 5 file CSV trong sql/data vào shop_db bằng LOAD DATA LOCAL INFILE.

Đường dẫn file tự tính từ vị trí của script nên chạy được trên mọi máy,
không cần sửa tay như sql/data/03_load_bigdata.sql (dùng đường dẫn tuyệt đối).

Yêu cầu:
  - đã tạo bảng (sql/schema/02_create_tables.sql) và sinh CSV (python/generate_data.py)
  - MySQL server bật local_infile:  SET GLOBAL local_infile = 1;  (quyền root)

Chạy từ thư mục gốc dự án:  python python/load_data.py
"""
import time
from pathlib import Path

import mysql.connector
from config import DB_CONFIG

DATA = Path(__file__).resolve().parent.parent / "sql" / "data"

# (tên bảng, thứ tự cột trong file CSV)
TABLES = [
    ("categories", ["category_id", "category_name"]),
    ("customers", ["customer_id", "full_name", "email", "phone", "city", "created_at"]),
    ("products", ["product_id", "product_name", "category_id", "price", "stock", "created_at"]),
    ("orders", ["order_id", "customer_id", "order_date", "status", "payment_method", "total_amount"]),
    ("order_items", ["order_item_id", "order_id", "product_id", "quantity", "unit_price"]),
]


def main():
    missing = [t for t, _ in TABLES if not (DATA / f"{t}.csv").exists()]
    if missing:
        raise SystemExit(f"Thiếu file CSV: {', '.join(m + '.csv' for m in missing)}. "
                         "Hãy chạy trước: python python/generate_data.py")

    cfg = dict(DB_CONFIG)
    cfg["allow_local_infile"] = True
    conn = mysql.connector.connect(**cfg)
    cur = conn.cursor()
    cur.execute("SET unique_checks = 0")
    cur.execute("SET foreign_key_checks = 0")

    t_all = time.time()
    for table, cols in TABLES:
        path = (DATA / f"{table}.csv").as_posix()
        sql = (f"LOAD DATA LOCAL INFILE '{path}' INTO TABLE {table} CHARACTER SET utf8mb4 "
               "FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' "
               "LINES TERMINATED BY '\\n' IGNORE 1 LINES "
               f"({', '.join(cols)})")
        t = time.time()
        cur.execute(sql)
        conn.commit()
        print(f"  {table}: {cur.rowcount:,} dòng ({time.time() - t:.1f}s)", flush=True)

    cur.execute("SET unique_checks = 1")
    cur.execute("SET foreign_key_checks = 1")
    for table, _ in TABLES:
        cur.execute(f"ANALYZE TABLE {table}")
        cur.fetchall()

    cur.close()
    conn.close()
    print(f"Hoàn tất sau {time.time() - t_all:.0f}s.")


if __name__ == "__main__":
    main()