--Ce test vérifie qu'il n'y a pas de doublons de localisation_key
SELECT
    localisation_key,
    COUNT(*)
FROM {{ ref('dim_venues') }}
GROUP BY localisation_key
HAVING COUNT(*) > 1