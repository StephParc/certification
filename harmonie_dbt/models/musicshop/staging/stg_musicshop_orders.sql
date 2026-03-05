-- stg_musicshop_orders.sql
WITH raw_data AS (
    SELECT * FROM {{ source('raw_musicshop', 'raw_orders') }}
),
country_map AS (
    SELECT * FROM {{ ref('countries') }}
),
renamed AS (
    SELECT
        order_id,
        customer_id,
        system_source,
        name AS customer_name,
        address,
        postal_code,
        email,
        country,
        profile,
        order_date,
        partition_id AS product_id,
        titre AS title,
        ref_editeur AS editor_referency,
        edition AS editor_name,
        quantity,
        local_price
    FROM raw_data
)
SELECT r.*,
    CAST(r.order_date + CAST(c.utc_offset AS INTERVAL) AS DATE) AS date_key
FROM renamed AS r
LEFT JOIN country_map AS c
    ON c.country = r.country