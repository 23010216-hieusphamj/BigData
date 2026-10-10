USE shop_db;

-- ===== BƯỚC 1: index đơn =====
-- Q1, Q4, Q7: lọc và sắp xếp theo ngày đặt hàng
CREATE INDEX idx_orders_order_date  ON orders (order_date);
-- Q3, Q8: join từ khách hàng sang đơn hàng
CREATE INDEX idx_orders_customer_id ON orders (customer_id);
-- Q3: tìm khách theo email
CREATE INDEX idx_customers_email    ON customers (email);

ANALYZE TABLE orders, customers;