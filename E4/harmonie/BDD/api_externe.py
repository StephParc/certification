# api_externe.py
import requests

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
    if identity:
        url = f"https://musicbrainz.org/ws/2/artist/?query={identity}&fmt=json"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data["artists"]:               
                artists = data["artists"][0]
                if "isnis" in artists:
                    artist = artists
                else:
                    artist = data["artists"][1]

                identity_list = artist["sort-name"].split(",") # "name" renvoie dans la langue -> pb pour les noms asiatiques
                nom = identity_list[0]
                if len(identity_list)>=2:
                    prenom = identity_list[1]
                else:
                    prenom = None
                pays = artist.get("area", {}).get("name")
                IPI = ",".join(artist.get("ipis")) if artist.get("ipis") else None
                ISNI = ",".join(artist.get("isnis")) if artist.get("isnis") else None

                auteur = {"Nom": nom, "Prénom": prenom, "Pays": pays, "IPI": IPI, "ISNI": ISNI}
            else:
                auteur = None
        else:
            print("Erreur :", response.status_code)

    else:
        auteur = None
        print("pas d'identité")

    return auteur

## Exemples pour tester l'API

# print(get_api_externe("ravel"))
# print(get_api_externe("Satoshi Yagisawa"))
# print(get_api_externe("MIMI"))
# print(get_api_externe("ijdzoij"))
# print(get_api_externe("erik satie"))
# print(get_api_externe("nirvana"))
# print(get_api_externe(None))
# print(get_api_externe(""))
    