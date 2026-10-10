USE shop_db;

-- @Q1 | Đơn hoàn tất trong tháng 1/2025 | Vấn đề: quét toàn bảng orders
SELECT order_id, customer_id, order_date, total_amount
FROM orders
WHERE order_date >= '2025-01-01'
  AND order_date <  '2025-02-01'
  AND status = 'completed';

-- @Q2 | Doanh thu tháng 3/2025 | Vấn đề: hàm YEAR(), MONTH() bọc cột order_date
SELECT COUNT(*) AS so_don, SUM(total_amount) AS doanh_thu
FROM orders
WHERE YEAR(order_date) = 2025
  AND MONTH(order_date) = 3
  AND status = 'completed';

-- @Q3 | Tìm khách theo email và các đơn hàng | Vấn đề: không có index email, join orders không có index customer_id
SELECT c.customer_id, c.full_name, c.email,
       o.order_id, o.order_date, o.total_amount
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
WHERE c.email LIKE 'user12345@%';

-- @Q4 | Doanh thu theo tháng và danh mục năm 2025 | Vấn đề: join 4 bảng không có index
SELECT DATE_FORMAT(o.order_date, '%Y-%m') AS thang,
       cat.category_name,
       SUM(oi.quantity * oi.unit_price) AS doanh_thu
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p     ON p.product_id = oi.product_id
JOIN categories cat ON cat.category_id = p.category_id
WHERE o.order_date >= '2025-01-01'
  AND o.order_date <  '2026-01-01'
  AND o.status = 'completed'
GROUP BY thang, cat.category_name
ORDER BY thang, doanh_thu DESC;

-- @Q5 | Top 3 sản phẩm doanh thu cao nhất mỗi danh mục | Vấn đề: quét toàn bộ order_items, window function
WITH product_rev AS (
    SELECT p.product_id, p.product_name, p.category_id,
           SUM(oi.quantity * oi.unit_price) AS doanh_thu
    FROM order_items oi
    JOIN products p ON p.product_id = oi.product_id
    GROUP BY p.product_id, p.product_name, p.category_id
),
ranked AS (
    SELECT product_rev.*,
           ROW_NUMBER() OVER (PARTITION BY category_id ORDER BY doanh_thu DESC) AS hang
    FROM product_rev
)
SELECT c.category_name, r.product_name, r.doanh_thu, r.hang
FROM ranked r
JOIN categories c ON c.category_id = r.category_id
WHERE r.hang <= 3
ORDER BY c.category_name, r.hang;

-- @Q6 | Sản phẩm có giá cao hơn giá trung bình của danh mục | Vấn đề: subquery tương quan chạy lại cho từng sản phẩm
SELECT p.product_id, p.product_name, p.category_id, p.price
FROM products p
WHERE p.price > (
    SELECT AVG(p2.price)
    FROM products p2
    WHERE p2.category_id = p.category_id
);

-- @Q7 | Phân trang sâu: trang thứ 50.001 (20 đơn mỗi trang) | Vấn đề: sắp xếp 2 triệu dòng, bỏ 1 triệu dòng đầu
SELECT order_id, customer_id, order_date, total_amount
FROM orders
ORDER BY order_date DESC, order_id DESC
LIMIT 20 OFFSET 1000000;

-- @Q8 | Top 10 khách chi tiêu nhiều nhất ở Hà Nội | Vấn đề: lọc thành phố, join orders không index
SELECT c.customer_id, c.full_name, c.city,
       COUNT(o.order_id)   AS so_don,
       SUM(o.total_amount) AS tong_chi_tieu
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
WHERE c.city = 'Hà Nội'
  AND o.status = 'completed'
GROUP BY c.customer_id, c.full_name, c.city
ORDER BY tong_chi_tieu DESC
LIMIT 10;