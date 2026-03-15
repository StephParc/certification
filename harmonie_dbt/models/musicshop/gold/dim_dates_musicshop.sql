-- dim_dates_musicshop.sql
WITH silver AS(
    SELECT DISTINCT
        date_key
    FROM {{ ref('int_orders_converted') }}
)
SELECT
    date_key,
    EXTRACT(YEAR FROM date_key)::integer AS annee,
    EXTRACT(MONTH FROM date_key)::integer AS mois,
    EXTRACT(DAY FROM date_key)::integer AS jour
FROM silver