-- dim_genres.sql
WITH staging AS(
    SELECT DISTINCT
        genre,
        genre_id,
        sous_categorie,
        sous_categorie_id  
    FROM {{ ref('stg_ticketmaster') }}
)
SELECT 
    {{ dbt_utils.generate_surrogate_key(['genre_id','sous_categorie_id']) }} AS genre_key,
    genre,
    sous_categorie
FROM staging
