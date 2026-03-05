-- dim_customers.sql
SELECT
    {{ dbt_utils.generate_surrogate_key(['customer_id','system_source']) }} AS customer_key,
    customer_id,
    system_source,
    name AS customer_name,
    email,
    country,
    profile,
    dbt_valid_from AS valid_from,
    dbt_valid_to AS valid_to,
    CASE 
        WHEN dbt_valid_to IS NULL THEN TRUE 
        ELSE FALSE 
    END AS is_current
FROM {{ ref('snp_customers') }}