USE shop_db;
DROP INDEX idx_orders_status_date_cov ON orders;
DROP INDEX idx_oi_order_cov            ON order_items;
DROP INDEX idx_oi_product_cov          ON order_items;
DROP INDEX idx_customers_city_name     ON customers;
DROP INDEX idx_orders_cust_status_amt  ON orders;
CREATE INDEX idx_orders_customer_id    ON orders (customer_id);