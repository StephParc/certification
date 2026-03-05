-- fact_orders.sql
{{ config(
    materialized='table',
    post_hook=[
        "ALTER TABLE {{ this }} ADD CONSTRAINT fk_fact_date FOREIGN KEY (date_key) REFERENCES {{ ref('dim_dates_musicshop') }} (date_key)",
        "ALTER TABLE {{ this }} ADD CONSTRAINT fk_fact_product FOREIGN KEY (product_id) REFERENCES {{ ref('dim_products') }} (product_id)",
        "ALTER TABLE {{ this }} ADD CONSTRAINT fk_fact_customer FOREIGN KEY (customer_key) REFERENCES {{ ref('dim_customers') }} (customer_key)",
        "ALTER Table {{ this }} ENABLE ROW LEVEL SECURITY",
        "DROP POLICY IF EXISTS analyst_all_policy ON {{ this }}",
        "CREATE POLICY analyst_all_policy ON {{ this }} TO analyst_group USING (true)",
        "DROP POLICY IF EXISTS editor_visibility_policy ON {{ this }}",
        "CREATE POLICY editor_visibility_policy ON {{ this }} TO editor_role 
        USING (
            product_id IN (
                SELECT product_id
                FROM {{ ref('dim_products') }}
                WHERE editor_name = (
                    SELECT editor_name
                    FROM public.editor_metadata
                    WHERE db_user = current_user
                )
            )
        )",
        "GRANT SELECT ON {{ ref('dim_products') }} TO editor_role",
        "GRANT SELECT ON public.editor_metadata TO editor_role"
    ]
) }}

WITH silver_orders AS (
    SELECT * FROM {{ ref('int_orders_converted') }}
)

SELECT
    order_id,
    customer_key,
    customer_id,
    product_id,
    date_key,
    quantity,
    currency_code,
    local_price,
    local_amount,
    euro_price,
    euro_amount
FROM silver_orders
