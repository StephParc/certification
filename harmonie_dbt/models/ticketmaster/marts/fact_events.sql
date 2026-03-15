-- fact_events.sql
{{ config(
    materialized='table',
    post_hook=[
        "ALTER TABLE {{ this }} ADD CONSTRAINT fk_fact_date FOREIGN KEY (date_key) REFERENCES {{ ref('dim_dates') }} (date_key)",
        "ALTER TABLE {{ this }} ADD CONSTRAINT fk_fact_genre FOREIGN KEY (genre_key) REFERENCES {{ ref('dim_genres') }} (genre_key)",
        "ALTER TABLE {{ this }} ADD CONSTRAINT fk_fact_venue FOREIGN KEY (localisation_key) REFERENCES {{ ref('dim_venues') }} (localisation_key)"
    ]
) }}
SELECT DISTINCT
    event_key,
    event_nom,
    {{ dbt_utils.generate_surrogate_key(['event_date','event_heure']) }} AS date_key,
    {{ dbt_utils.generate_surrogate_key(['genre_id','sous_categorie_id']) }} AS genre_key,
    {{ dbt_utils.generate_surrogate_key(['pays','etat','ville']) }} AS localisation_key,
    1 AS nb_events
FROM {{ ref('stg_ticketmaster') }}