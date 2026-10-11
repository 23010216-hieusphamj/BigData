USE shop_db;

DROP TABLE IF EXISTS orders_w0, orders_w3, order_items_w0, order_items_w2;

-- orders_w3 và order_items_w2 giữ nguyên toàn bộ index hiện tại
CREATE TABLE orders_w3      LIKE orders;
CREATE TABLE order_items_w2 LIKE order_items;

-- orders_w0 và order_items_w0 chỉ giữ khóa chính
CREATE TABLE orders_w0      LIKE orders;
DROP INDEX idx_orders_order_date      ON orders_w0;
DROP INDEX idx_orders_status_date_cov ON orders_w0;
DROP INDEX idx_orders_cust_status_amt ON orders_w0;

CREATE TABLE order_items_w0 LIKE order_items;
DROP INDEX idx_oi_order_cov   ON order_items_w0;
DROP INDEX idx_oi_product_cov ON order_items_w0;