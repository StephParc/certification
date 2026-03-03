-- rapport_mensuel.sql

SELECT
    d.annee,
    d.mois,
    g.genre,
    g.sous_categorie,
    SUM(nb_events) as total_concerts
FROM {{ ref('fact_events') }} f
JOIN {{ ref('dim_dates') }} d ON f.date_key = d.date_key
JOIN {{ ref('dim_genres') }} g ON f.genre_key = g.genre_key
GROUP BY d.annee, d.mois, g.genre, g.sous_categorie
ORDER BY d.annee, d.mois, g.genre, total_concerts DESC