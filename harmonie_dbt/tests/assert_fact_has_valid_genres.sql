-- Vérifie que chaque événement a un genre qui existe bien dans la dimension
SELECT
    f.event_key
FROM {{ ref('fact_events') }} f
LEFT JOIN {{ ref('dim_genres') }} g 
    ON f.genre_key = g.genre_key
WHERE g.genre_key IS NULL