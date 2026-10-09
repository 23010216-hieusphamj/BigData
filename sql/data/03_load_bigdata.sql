USE shop_db;

SET autocommit = 0;
SET unique_checks = 0;
SET foreign_key_checks = 0;

LOAD DATA LOCAL INFILE 'E:/BigData/sql/data/categories.csv'
INTO TABLE categories CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n' IGNORE 1 LINES
(category_id, category_name);

LOAD DATA LOCAL INFILE 'E:/BigData/sql/data/customers.csv'
INTO TABLE customers CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n' IGNORE 1 LINES
(customer_id, full_name, email, phone, city, created_at);

LOAD DATA LOCAL INFILE 'E:/BigData/sql/data/products.csv'
INTO TABLE products CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n' IGNORE 1 LINES
(product_id, product_name, category_id, price, stock, created_at);

LOAD DATA LOCAL INFILE 'E:/BigData/sql/data/orders.csv'
INTO TABLE orders CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n' IGNORE 1 LINES
(order_id, customer_id, order_date, status, payment_method, total_amount);

LOAD DATA LOCAL INFILE 'E:/BigData/sql/data/order_items.csv'
INTO TABLE order_items CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n' IGNORE 1 LINES
(order_item_id, order_id, product_id, quantity, unit_price);

COMMIT;
SET unique_checks = 1;
SET foreign_key_checks = 1;
SET autocommit = 1;

ANALYZE TABLE categories, customers, products, orders, order_items;