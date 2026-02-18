-- stg_ticketmaster.sql

WITH raw_data AS (
    SELECT
        payload,
        inserted_at,
        file_name
    FROM {{ source('raw_ticketmaster', 'ticketmaster_events') }}
),
extracted AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key([
            "payload->>'id'",
            "payload->'dates'->'start'->>'localDate'"
        ]) }} AS event_key,
        payload->>'id' AS event_id,
        payload->>'name' AS event_nom,
        (payload->'dates'->'start'->>'localDate')::DATE AS event_date,
        (payload->'dates'->'start'->>'localTime')::TIME AS event_heure,
        payload->'classifications'->0->'genre'->>'id' AS genre_id,
        payload->'classifications'->0->'genre'->>'name' AS genre,
        payload->'classifications'->0->'subGenre'->>'id' AS sous_categorie_id,
        payload->'classifications'->0->'subGenre'->>'name' AS sous_categorie,
        payload->'_embedded'->'venues'->0->>'name' AS lieu,
        payload->'_embedded'->'venues'->0->>'postalCode' AS code_postal,
        payload->'_embedded'->'venues'->0->'city'->>'name' AS ville,
        payload->'_embedded'->'venues'->0->'state'->>'name' AS etat,
        payload->'_embedded'->'venues'->0->'country'->>'name' AS pays,
        payload->'_embedded'->'venues'->0->'address'->>'line1' AS adresse,
        CASE 
            WHEN (payload->'_embedded'->'venues'->0->'location'->>'latitude')='0' THEN NULL
            ELSE (payload->'_embedded'->'venues'->0->'location'->>'latitude')::FLOAT
        END AS latitude,
        CASE
            WHEN (payload->'_embedded'->'venues'->0->'location'->>'longitude')='0' THEN NULL
            ELSE (payload->'_embedded'->'venues'->0->'location'->>'longitude')::FLOAT 
        END AS longitude
    FROM raw_data
)
SELECT DISTINCT * FROM extracted
WHERE event_id IS NOT NULL 
    AND genre IS NOT NULL