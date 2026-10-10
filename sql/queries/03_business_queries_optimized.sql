USE shop_db;

-- @Q2 | Doanh thu tháng 3/2025 (viết lại) | Bỏ hàm bọc cột, dùng khoảng ngày để tận dụng index
SELECT COUNT(*) AS so_don, SUM(total_amount) AS doanh_thu
FROM orders
WHERE order_date >= '2025-03-01'
  AND order_date <  '2025-04-01'
  AND status = 'completed';

-- @Q5 | Top 3 sản phẩm mỗi danh mục (viết lại) | Gom nhóm theo product_id trước khi join, bỏ cột chuỗi khỏi GROUP BY
WITH product_rev AS (
    SELECT oi.product_id,
           SUM(oi.quantity * oi.unit_price) AS doanh_thu
    FROM order_items oi
    GROUP BY oi.product_id
),
ranked AS (
    SELECT p.category_id, p.product_name, r.doanh_thu,
           ROW_NUMBER() OVER (PARTITION BY p.category_id ORDER BY r.doanh_thu DESC) AS hang
    FROM product_rev r
    JOIN products p ON p.product_id = r.product_id
)
SELECT c.category_name, ranked.product_name, ranked.doanh_thu, ranked.hang
FROM ranked
JOIN categories c ON c.category_id = ranked.category_id
WHERE ranked.hang <= 3
ORDER BY c.category_name, ranked.hang;

-- @Q6A | Sản phẩm giá cao hơn trung bình danh mục (JOIN) | Tính trung bình mỗi danh mục một lần rồi join
SELECT p.product_id, p.product_name, p.category_id, p.price
FROM products p
JOIN (
    SELECT category_id, AVG(price) AS avg_price
    FROM products
    GROUP BY category_id
) a ON a.category_id = p.category_id
WHERE p.price > a.avg_price;

-- @Q6B | Sản phẩm giá cao hơn trung bình danh mục (window) | AVG() OVER, chỉ quét bảng một lần
SELECT product_id, product_name, category_id, price
FROM (
    SELECT product_id, product_name, category_id, price,
           AVG(price) OVER (PARTITION BY category_id) AS avg_price
    FROM products
) t
WHERE price > avg_price;

-- @Q7A | Phân trang sâu (keyset) | Bắt đầu sau dòng cuối của trang trước, không dùng OFFSET
SELECT order_id, customer_id, order_date, total_amount
FROM orders
WHERE order_date < '2022-12-31 14:54:45'
   OR (order_date = '2022-12-31 14:54:45' AND order_id < 1000001)
ORDER BY order_date DESC, order_id DESC
LIMIT 20;

-- @Q7B | Phân trang sâu (deferred join) | Vẫn dùng OFFSET nhưng chỉ đi qua index, rồi mới tra 20 dòng đầy đủ
SELECT o.order_id, o.customer_id, o.order_date, o.total_amount
FROM orders o
JOIN (
    SELECT order_id
    FROM orders
    ORDER BY order_date DESC, order_id DESC
    LIMIT 20 OFFSET 1000000
) t ON t.order_id = o.order_id
ORDER BY o.order_date DESC, o.order_id DESC;