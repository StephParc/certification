-- dim_products.sql
WITH products_unique AS (
    SELECT DISTINCT
        product_id,
        title,
        editor_referency,
        editor_name
    FROM {{ ref('int_orders_converted') }}
)

SELECT * FROM products_unique