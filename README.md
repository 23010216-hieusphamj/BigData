# Tối ưu SQL cho Big Data trên MySQL

Bài tập lớn học phần **Tích hợp và phân tích dữ liệu lớn**
Đề tài: **SQL và cơ sở dữ liệu - Tối ưu SQL, từ câu truy vấn đến execution plan**

- Sinh viên: (điền họ tên, mã sinh viên)
- Lớp / Giảng viên: (điền)

## Mục tiêu
Đo và so sánh hiệu năng các truy vấn nghiệp vụ trên tập dữ liệu hàng triệu dòng
trước và sau khi tối ưu (index, viết lại truy vấn, partitioning, bảng tổng hợp),
dựa trên phân tích execution plan bằng `EXPLAIN ANALYZE`.

## Môi trường
- MySQL 8.0.46 (InnoDB)
- Python 3, thư viện: mysql-connector-python, pandas, matplotlib
- Công cụ: MySQL Workbench (Visual Explain), VS Code, Git

## Cấu trúc thư mục
| Thư mục | Nội dung |
|---|---|
| `sql/schema/` | Script tạo database, bảng, index |
| `sql/data/` | Script nạp dữ liệu (file CSV được sinh ra, không đưa lên Git) |
| `sql/queries/` | Truy vấn trước và sau tối ưu |
| `python/` | Sinh dữ liệu, kiểm tra kết nối, benchmark |
| `results/` | Execution plan, ảnh Visual Explain, bảng và biểu đồ kết quả, ERD |
| `report/`, `slides/` | Báo cáo Word và slide thuyết trình |

## Cách chạy
1. Tạo môi trường Python:
   `python -m venv .venv` rồi `.venv\Scripts\activate` và `pip install -r python\requirements.txt`
2. Sao chép `python/config.example.py` thành `python/config.py` và điền mật khẩu.
3. Bật nạp file cục bộ trong MySQL (quyền root): `SET GLOBAL local_infile = 1;`
4. Tạo database: `mysql -u root -p < sql/schema/01_create_database.sql`
5. Tạo bảng: `mysql -u bt_user -p shop_db -e "source sql/schema/02_create_tables.sql"`
6. Sinh dữ liệu: `python python/generate_data.py`
7. Nạp dữ liệu: `mysql --local-infile=1 -u bt_user -p shop_db -e "source sql/data/03_load_bigdata.sql"`

## Tiến độ
- [x] Giai đoạn 1: Chuẩn bị môi trường
- [ ] Giai đoạn 2: Schema và dữ liệu
- [ ] Giai đoạn 3-4: Truy vấn chưa tối ưu và đo baseline
- [ ] Giai đoạn 5: Tối ưu và đo lại
- [ ] Giai đoạn 6-7: Tổng hợp, báo cáo, slide