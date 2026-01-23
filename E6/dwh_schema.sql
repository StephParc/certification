-- Create Tables for ShopNow DWH

-- 1. dim_customer
DROP TABLE IF EXISTS dim_customer;
CREATE TABLE dim_customer (
    customer_id VARCHAR(50) PRIMARY KEY,
    name        NVARCHAR(255),
    email       NVARCHAR(255),
    address     NVARCHAR(500),
    city        NVARCHAR(100),
    country     NVARCHAR(100)
);

-- 2. dim_product
DROP TABLE IF EXISTS dim_product;
CREATE TABLE dim_product (
    technical_id        INT AUTOINCREMENT PRIMARY KEY,
    product_id          VARCHAR(50),
    name                NVARCHAR(255),
    category            NVARCHAR(100),
    unit_price          DECIMAL(18,2),
    commission_rate     DECIMAL(18,2),
    seller_id           VARCHAR(50),
    stock               INT,
    availibility_delay  INT
);

-- 3. dim_seller
DROP TABLE IF EXISTS dim_seller;
CREATE TABLE dim_seller (
    technical_id        INT AUTOINCREMENT PRIMARY KEY,
    seller_id           VARCHAR(50),
    email               NVARCHAR(255),
    address             NVARCHAR(500),
    city                NVARCHAR(100),
    country             NVARCHAR(100),
    membership_tier     VARCHAR(10),
    membership_discount DECIMAL(18,2),
    account_status      VARCHAR(15)      
);

-- 4. fact_order
DROP TABLE IF EXISTS fact_order;
CREATE TABLE fact_order (
    order_id        VARCHAR(50),
    product_id      VARCHAR(50),
    customer_id     VARCHAR(50),
    seller_id       VARCHAR(50),
    quantity        INT,
    unit_price      DECIMAL(18, 2),
    status          NVARCHAR(50),
    order_timestamp DATETIME
);

-- 5. fact_clickstream
DROP TABLE IF EXISTS fact_clickstream;
CREATE TABLE fact_clickstream (
    event_id        VARCHAR(50) PRIMARY KEY,
    session_id      VARCHAR(50),
    user_id         VARCHAR(50),
    url             NVARCHAR(MAX),
    event_type      NVARCHAR(50),
    event_timestamp DATETIME
);
