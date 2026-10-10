USE shop_db;
DROP INDEX idx_orders_order_date  ON orders;
DROP INDEX idx_orders_customer_id ON orders;
DROP INDEX idx_customers_email    ON customers;