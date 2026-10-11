USE shop_db;

DROP TABLE IF EXISTS sales_monthly_category;
DROP TABLE IF EXISTS product_revenue;
DROP TABLE IF EXISTS customer_spend;

-- Doanh thu đơn hoàn tất theo tháng và danh mục (phục vụ Q4)
CREATE TABLE sales_monthly_category (
    thang       CHAR(7)           NOT NULL,
    category_id SMALLINT UNSIGNED NOT NULL,
    doanh_thu   DECIMAL(18,2)     NOT NULL,
    PRIMARY KEY (thang, category_id)
) ENGINE=InnoDB;

-- Doanh thu mỗi sản phẩm trên toàn bộ chi tiết đơn (phục vụ Q5)
CREATE TABLE product_revenue (
    product_id INT UNSIGNED  NOT NULL,
    doanh_thu  DECIMAL(18,2) NOT NULL,
    PRIMARY KEY (product_id)
) ENGINE=InnoDB;

-- Số đơn và chi tiêu của mỗi khách, chỉ tính đơn hoàn tất (phục vụ Q8)
CREATE TABLE customer_spend (
    customer_id   INT UNSIGNED  NOT NULL,
    so_don        INT           NOT NULL,
    tong_chi_tieu DECIMAL(18,2) NOT NULL,
    PRIMARY KEY (customer_id)
) ENGINE=InnoDB;

INSERT INTO sales_monthly_category
SELECT DATE_FORMAT(o.order_date, '%Y-%m'), p.category_id,
       SUM(oi.quantity * oi.unit_price)
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p     ON p.product_id = oi.product_id
WHERE o.status = 'completed'
GROUP BY DATE_FORMAT(o.order_date, '%Y-%m'), p.category_id;

INSERT INTO product_revenue
SELECT product_id, SUM(quantity * unit_price)
FROM order_items
GROUP BY product_id;

INSERT INTO customer_spend
SELECT customer_id, COUNT(*), SUM(total_amount)
FROM orders
WHERE status = 'completed'
GROUP BY customer_id;

ANALYZE TABLE sales_monthly_category, product_revenue, customer_spend;