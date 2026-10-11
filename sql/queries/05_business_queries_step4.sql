USE shop_db;

-- @Q4S | Doanh thu theo tháng và danh mục 2025 (đọc bảng tổng hợp)
SELECT s.thang, cat.category_name, s.doanh_thu
FROM sales_monthly_category s
JOIN categories cat ON cat.category_id = s.category_id
WHERE s.thang >= '2025-01' AND s.thang <= '2025-12'
ORDER BY s.thang, s.doanh_thu DESC;

-- @Q5S | Top 3 sản phẩm mỗi danh mục (đọc bảng tổng hợp)
SELECT c.category_name, x.product_name, x.doanh_thu, x.hang
FROM (
    SELECT p.category_id, p.product_name, r.doanh_thu,
           ROW_NUMBER() OVER (PARTITION BY p.category_id ORDER BY r.doanh_thu DESC) AS hang
    FROM product_revenue r
    JOIN products p ON p.product_id = r.product_id
) x
JOIN categories c ON c.category_id = x.category_id
WHERE x.hang <= 3
ORDER BY c.category_name, x.hang;

-- @Q8S | Top 10 khách chi tiêu nhiều nhất ở Hà Nội (đọc bảng tổng hợp)
SELECT c.customer_id, c.full_name, c.city,
       s.so_don, s.tong_chi_tieu
FROM customers c
JOIN customer_spend s ON s.customer_id = c.customer_id
WHERE c.city = 'Hà Nội'
ORDER BY s.tong_chi_tieu DESC
LIMIT 10;

-- @Q1P | Đơn hoàn tất tháng 1/2025 trên bảng chia partition, chưa có index phụ
SELECT order_id, customer_id, order_date, total_amount
FROM orders_part
WHERE order_date >= '2025-01-01'
  AND order_date <  '2025-02-01'
  AND status = 'completed';

-- @Q2P | Doanh thu tháng 3/2025 trên bảng chia partition, chưa có index phụ
SELECT COUNT(*) AS so_don, SUM(total_amount) AS doanh_thu
FROM orders_part
WHERE order_date >= '2025-03-01'
  AND order_date <  '2025-04-01'
  AND status = 'completed';