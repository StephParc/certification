-- snapshot_customers.sql
{% snapshot snp_customers %}

{{
    config(
        target_schema='snapshots',
        unique_key="'DB_' || upper(left(country,3)) || '-' || customer_id",
        strategy='check',
        check_cols=['profile', 'address', 'email'],
    )
}}

SELECT *,
    'DB_' || upper(left(country, 3)) AS system_source
FROM {{ source('raw_musicshop', 'customer') }}

{% endsnapshot %}