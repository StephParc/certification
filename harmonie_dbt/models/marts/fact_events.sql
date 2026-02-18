-- fact_events.sql
SELECT
    event_key,
    event_nom,
    {{ dbt_utils.generate_surrogate_key(['event_date','event_heure']) }} AS date_key,
    {{ dbt_utils.generate_surrogate_key(['genre_id','sous_categorie_id']) }} AS genre_key,
    {{ dbt_utils.generate_surrogate_key(['pays','etat','ville']) }} AS localisation_key,
    1 AS nb_events
FROM {{ ref('stg_ticketmaster') }}