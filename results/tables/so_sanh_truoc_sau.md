| Truy vấn | Kỹ thuật | Baseline (s) | Cuối (s) | Tăng tốc (TB) | Tăng tốc (trung vị) |
|---|---|---|---|---|---|
| Q1 | Covering index (status, order_date, ...) | 4,612 ± 0,3928 | 0,0694 ± 0,0145 | 66 lần | 66 lần |
| Q2 | Bỏ hàm bọc cột + covering index | 3,543 ± 0,4901 | 0,0301 ± 0,0058 | 118 lần | 104 lần |
| Q3 | Index email + index theo customer_id | 19,71 ± 3,176 | 0,0022 ± 0,0014 | 8.961 lần | 13.764 lần |
| Q4 | Covering index (chỉ dùng index) | 101,56 ± 9,812 | 21,00 ± 2,106 | 4,8 lần | 4,9 lần |
| Q4S | Bảng tổng hợp | 101,56 ± 9,812 | 0,0107 ± 0,0029 | 9.492 lần | 10.277 lần |
| Q5 | Gom nhóm trước + covering index | 250,71 ± 2,530 | 6,107 ± 1,476 | 41 lần | 41 lần |
| Q5S | Bảng tổng hợp | 250,71 ± 2,530 | 0,1800 ± 0,0622 | 1.393 lần | 1.473 lần |
| Q6A | Viết lại bằng JOIN | 112,67 ± 7,162 | 0,0774 ± 0,0405 | 1.456 lần | 2.148 lần |
| Q6B | Viết lại bằng window function | 112,67 ± 7,162 | 0,1105 ± 0,0581 | 1.020 lần | 1.037 lần |
| Q7A | Keyset + FORCE INDEX | 6,511 ± 0,5848 | 0,0024 ± 0,0015 | 2.713 lần | 3.554 lần |
| Q7B | Deferred join | 6,511 ± 0,5848 | 0,9611 ± 0,2040 | 6,8 lần | 7,1 lần |
| Q8 | Composite + covering index | 22,37 ± 1,452 | 3,657 ± 0,5635 | 6,1 lần | 6,0 lần |
| Q8S | Bảng tổng hợp | 22,37 ± 1,452 | 0,4331 ± 0,1196 | 52 lần | 48 lần |
