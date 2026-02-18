-- dim_venues.sql
SELECT DISTINCT
    {{ dbt_utils.generate_surrogate_key(['pays','etat','ville']) }} AS localisation_key,
    pays,
    etat,
    ville
FROM {{ ref('stg_ticketmaster') }}