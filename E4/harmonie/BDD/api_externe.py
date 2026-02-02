# api_externe.py
import requests
import csv
import sys
import os
import time
from requests.exceptions import RequestException, Timeout

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from utils.S3_utils import upload_file, get_s3_client

# Fichier de rejet pour les auteurs (MusicBrainz)
REJET_AUTEURS_FILE = "rejets_auteurs_api.csv"

def log_rejection_auteur(identity, reason):
    """Enregistre l'échec de récupération de l'auteur."""
    file_exists = os.path.isfile(REJET_AUTEURS_FILE)
    try:
        with open(REJET_AUTEURS_FILE, "a", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["identity_recherchee", "raison_rejet"])
            writer.writerow([identity, reason])
    except Exception as e:
        print(f"Erreur lors de l'écriture du rejet : {e}")

def get_api_externe(identity):
    """
    Retrieve artist information from the MusicBrainz API based on the provided identity.

    This function queries the MusicBrainz API to fetch details about an artist. It constructs a request
    using the provided identity (artist name) and processes the response to extract relevant information
    such as the artist's name, country, IPI, and ISNI identifiers.

    Args:
        identity (str): The name of the artist to search for in the MusicBrainz API.

    Returns:
        dict: A dictionary containing the artist's details, including:
            - Nom (str): The last name of the artist.
            - Prénom (str): The first name of the artist, if available.
            - Pays (str): The country associated with the artist.
            - IPI (str): A comma-separated string of IPI identifiers, if available.
            - ISNI (str): A comma-separated string of ISNI identifiers, if available.
        None: If the API request fails or no artist information is found.
    """
    
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0"
    }

    if not identity or str(identity).strip().lower() == "none":
        log_rejection_auteur("None/Vide", "Identité absente dans le fichier source")
        return None
    
    clean_identity_str = identity.strip()
    words_identity = set(clean_identity_str.lower().split())

    url = f"https://musicbrainz.org/ws/2/artist/?query={identity}&fmt=json"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        artists = data.get("artists", [])

        if not artists:
            log_rejection_auteur(clean_identity_str, "Aucun résultat trouvé sur MusicBrainz")
            return None

        # recherche de la meilleure correspondance
        selected_artist = None
        best_score = -1

        for a in artists[:3]:
            mb_name = a.get("name", "").lower()
            mb_sort_name_raw = a.get("sort-name", "").lower()
            mb_sort_name_clean = mb_sort_name_raw.replace(",", "")
            
            words_mb_name = set(mb_name.split())
            words_mb_sort = set(mb_sort_name_clean.split())

            if words_identity == words_mb_name or words_identity == words_mb_sort:
                current_score = 0
                if "," in mb_sort_name_raw: current_score += 10  
                if a.get("isnis"): current_score += 5        
                if a.get("ipis"): current_score += 5         
                if a.get("area"): current_score += 2         

                if current_score > best_score:
                    best_score = current_score
                    selected_artist = a
        
        if not selected_artist:
            log_rejection_auteur(clean_identity_str, "Nom trouvé mais correspondance incertaine (homonymes)")
            return None

        sort_name = selected_artist.get("sort-name", "")
        if "," in sort_name:
            # On sépare tout pour voir combien on a de morceaux
            parts = [p.strip() for p in sort_name.split(",")]
            
            if len(parts) == 3:
                # Cas "Nom, Particule, Prénom" (ex: Roost, van der, Jan)
                nom = f"{parts[1]} {parts[0]}" # "van der" + " " + "Roost"
                prenom = parts[2]              # "Jan"
            elif len(parts) == 2:
                # Cas "Nom, Prénom" (ex: Deleruyelle, Thierry)
                nom = parts[0]
                prenom = parts[1]
            else:
                # Cas complexe (plus de 3 parties), on prend le dernier comme prénom
                prenom = parts[-1]
                nom = " ".join(parts[:-1])
        else:
            # Pas de virgule (ex: Nirvana)
            nom = sort_name.strip()
            prenom = None

        return {
            "Nom": nom,
            "Prénom": prenom,
            "Pays": selected_artist.get("area", {}).get("name", None),
            "IPI": ",".join(selected_artist.get("ipis")) if selected_artist.get("ipis") else None,
            "ISNI": ",".join(selected_artist.get("isnis")) if selected_artist.get("isnis") else None
        }

    except (RequestException, Timeout) as e:
        log_rejection_auteur(clean_identity_str, f"Erreur réseau/API : {str(e)}")
        return None
    except Exception as e:
        log_rejection_auteur(clean_identity_str, f"Erreur inattendue : {str(e)}")
        return None

## Exemples pour tester l'API
if __name__ == "__main__":
    print("Test Satoshi:", get_api_externe("Satoshi Yagisawa"))
    print("Test Thierry Deleruyelle:", get_api_externe("Thierry Deleruyelle"))
    print("Test Jan van der Roost", get_api_externe("Jan van der Roost"))
    print("Test ijdzoij", get_api_externe("ijdzoij"))
    print("Test Nirvana", get_api_externe("nirvana"))
    print("Test Erik Satie", get_api_externe("erik satie"))
    print("Test Ravel", get_api_externe("ravel"))
    print("Test None:", get_api_externe(None))
    print("Test vide", get_api_externe(""))