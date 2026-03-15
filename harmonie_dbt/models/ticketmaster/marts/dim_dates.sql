-- dim_dates.sql
WITH staging AS(
    SELECT DISTINCT
        event_date,
        event_heure
    FROM {{ ref('stg_ticketmaster') }}
)
SELECT
    {{ dbt_utils.generate_surrogate_key(['event_date','event_heure']) }} AS date_key,
    event_date,
    event_heure,
    EXTRACT(YEAR FROM event_date)::integer AS annee,
    EXTRACT(MONTH FROM event_date)::integer AS mois,
    EXTRACT(DAY FROM event_date)::integer AS jour,
    TO_CHAR(event_date, 'TMDay') AS jour_semaine,
    CASE
        WHEN event_heure BETWEEN '08:00:00' AND '12:00:00' THEN 'matin'
        WHEN event_heure BETWEEN '12:00:01' AND '16:30:00' THEN 'début après-midi'
        WHEN event_heure BETWEEN '16:30:01' AND '18:59:59' THEN 'fin après-midi'
        WHEN event_heure BETWEEN '19:00:00' AND '21:59:59' THEN 'soirée'
        WHEN event_heure >= '22:00:00' OR event_heure<= '07:59:59' THEN 'nocturne'
        ELSE NULL
    END AS tranche_horaire
FROM staging