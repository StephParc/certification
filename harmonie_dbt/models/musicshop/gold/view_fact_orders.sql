-- view_fact_orders.sql
{{ config(
    materialized='view'
)}}

SELECT 
    f.order_id,
    f.customer_key,
    f.customer_id,
    c.country,
    c.profile,
    f.product_id,
    p.title,
    p.editor_referency,
    p.editor_name,
    f.date_key,
    f.quantity,
    f.currency_code,
    f.local_price,
    f.local_amount,
    f.euro_price,
    f.euro_amount
FROM {{ ref('fact_orders') }} AS f
LEFT JOIN {{ ref('dim_customers') }} AS c
    ON f.customer_key=c.customer_key
    AND f.date_key >= CAST(c.valid_from AS DATE)
    AND (f.date_key < CAST(c.valid_to AS DATE) OR c.valid_to IS NULL)
LEFT JOIN {{ ref('dim_products') }} AS p
    ON f.product_id=p.product_id
LEFT JOIN {{ ref('dim_dates_musicshop') }} AS d
    ON f.date_key=d.date_key
    