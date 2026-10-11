# Chi phí ghi của index (nạp 500.000 dòng vào bảng thử nghiệm)

| Phép đo | Không index phụ (s) | Có index (s) | Tỷ lệ chậm hơn |
|---|---|---|---|
| INSERT 500.000 đơn, lần 1 | 29,125 | 62,672 | 2,15 lần |
| INSERT 500.000 đơn, lần 2 | 20,625 | 52,672 | 2,55 lần |
| **INSERT 500.000 đơn, trung bình** | **24,875** | **57,672** | **2,32 lần** |
| INSERT 500.000 dòng chi tiết, lần 1 | 25,719 | 46,765 | 1,82 lần |
| INSERT 500.000 dòng chi tiết, lần 2 | 25,672 | 57,093 | 2,22 lần |
| **INSERT 500.000 dòng chi tiết, trung bình** | **25,696** | **51,929** | **2,02 lần** |
| UPDATE 100.000 đơn (total_amount), một lần đo | 4,453 | 13,812 | 3,10 lần |

| Bảng thử nghiệm | Dòng thực tế | Dòng ước lượng (TABLE_ROWS) | Dữ liệu (MB) | Index (MB) | Index / dữ liệu |
|---|---|---|---|---|---|
| orders_w0 | 500.000 | 498.050 | 28,55 | 0,00 | 0% |
| orders_w3 | 500.000 | 498.937 | 28,55 | 48,67 | 170% |
| order_items_w0 | 500.000 | 499.365 | 19,55 | 0,00 | 0% |
| order_items_w2 | 500.000 | 499.365 | 19,55 | 36,11 | 185% |

Ghi chú:
- orders_w3 có 3 index phụ, order_items_w2 có 2 index phụ (đều là covering index như bước 3). Hai bảng _w0 chỉ có khóa chính.
- Dung lượng đo sau lần nạp thứ hai, trước khi xóa bảng thử nghiệm.
- Thời gian mỗi lệnh INSERT gồm cả việc đọc 500.000 dòng từ bảng nguồn (giống nhau ở cả hai biến thể), nên tỷ lệ chậm hơn thực sự của riêng việc ghi index hơi cao hơn số đo.
- Index được cập nhật dần khi INSERT chiếm nhiều dung lượng hơn index tạo một lần bằng CREATE INDEX (do tách trang), nên tỷ lệ index/dữ liệu ở bảng thử nghiệm cao hơn các bảng gốc ở bước 3 (136%).
- UPDATE chỉ đo một lần, trên dữ liệu nạp lần 1.