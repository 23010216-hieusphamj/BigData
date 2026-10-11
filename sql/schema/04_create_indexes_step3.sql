USE shop_db;

-- ===== 3A: covering index cho lọc theo trạng thái và ngày =====
-- Q1: cần status, order_date, customer_id, total_amount (order_id có sẵn trong mọi index)
-- Q2: cần status, order_date, total_amount
CREATE INDEX idx_orders_status_date_cov
    ON orders (status, order_date, customer_id, total_amount);
ANALYZE TABLE orders;
-- ===== 3B: covering index cho order_items =====
-- Q4: từ đơn hàng tìm các dòng chi tiết theo order_id, cần product_id, quantity, unit_price
CREATE INDEX idx_oi_order_cov
    ON order_items (order_id, product_id, quantity, unit_price);
-- Q5: gom nhóm theo product_id, cần quantity, unit_price
CREATE INDEX idx_oi_product_cov
    ON order_items (product_id, quantity, unit_price);
ANALYZE TABLE order_items;
-- ===== 3C: Q8 =====
-- tìm khách theo thành phố, đã phủ customer_id, full_name, city
CREATE INDEX idx_customers_city_name
    ON customers (city, full_name);
-- tìm đơn của từng khách theo trạng thái, đã phủ total_amount
CREATE INDEX idx_orders_cust_status_amt
    ON orders (customer_id, status, total_amount);

-- idx_orders_customer_id (chỉ có customer_id) nay là tiền tố của index trên, trở nên thừa
DROP INDEX idx_orders_customer_id ON orders;
ANALYZE TABLE customers, orders;