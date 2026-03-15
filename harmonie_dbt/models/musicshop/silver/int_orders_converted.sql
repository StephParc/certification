-- int_orders_converted.sql
WITH orders AS (
    SELECT *,
        quantity*local_price AS local_amount
    FROM {{ ref('stg_musicshop_orders') }}
),
currency_map AS (
    SELECT * FROM {{ ref('currencies') }}
),
countries_map AS (
    SELECT * FROM {{ ref('countries') }}
),
rates AS (
    SELECT * FROM {{ source('raw_musicshop','exchange_rates')}}
),
enriched AS (
    SELECT o.*,
        {{ dbt_utils.generate_surrogate_key(['o.customer_id','o.system_source']) }} AS customer_key,
        cu.currency_code,
        r.exchange_rate,
        round(o.local_price / r.exchange_rate, 2) AS euro_price,
        round(o.local_amount / r.exchange_rate, 2) AS euro_amount
    FROM orders AS o
    LEFT JOIN countries_map AS co
        ON o.country = co.country
    LEFT JOIN currency_map AS cu
        ON co.currency_code = cu.currency_code
    LEFT JOIN rates AS r
        ON cu.currency_code = r.currency_code
        AND CAST(o.order_date AS DATE) = r.date_key
)

SELECT * FROM enriched