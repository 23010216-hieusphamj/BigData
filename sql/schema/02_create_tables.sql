USE shop_db;

DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS categories;

CREATE TABLE categories (
    category_id   SMALLINT UNSIGNED NOT NULL,
    category_name VARCHAR(100)      NOT NULL,
    PRIMARY KEY (category_id)
) ENGINE=InnoDB;

CREATE TABLE customers (
    customer_id INT UNSIGNED NOT NULL,
    full_name   VARCHAR(100) NOT NULL,
    email       VARCHAR(150) NOT NULL,
    phone       VARCHAR(20)  NULL,
    city        VARCHAR(50)  NOT NULL,
    created_at  DATETIME     NOT NULL,
    PRIMARY KEY (customer_id)
) ENGINE=InnoDB;

CREATE TABLE products (
    product_id   INT UNSIGNED      NOT NULL,
    product_name VARCHAR(150)      NOT NULL,
    category_id  SMALLINT UNSIGNED NOT NULL,
    price        DECIMAL(10,2)     NOT NULL,
    stock        INT               NOT NULL,
    created_at   DATETIME          NOT NULL,
    PRIMARY KEY (product_id)
) ENGINE=InnoDB;

CREATE TABLE orders (
    order_id       INT UNSIGNED  NOT NULL,
    customer_id    INT UNSIGNED  NOT NULL,
    order_date     DATETIME      NOT NULL,
    status         VARCHAR(20)   NOT NULL,
    payment_method VARCHAR(20)   NOT NULL,
    total_amount   DECIMAL(12,2) NOT NULL,
    PRIMARY KEY (order_id)
) ENGINE=InnoDB;

CREATE TABLE order_items (
    order_item_id INT UNSIGNED      NOT NULL,
    order_id      INT UNSIGNED      NOT NULL,
    product_id    INT UNSIGNED      NOT NULL,
    quantity      SMALLINT UNSIGNED NOT NULL,
    unit_price    DECIMAL(10,2)     NOT NULL,
    PRIMARY KEY (order_item_id)
) ENGINE=InnoDB;