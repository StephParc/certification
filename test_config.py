import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def inspect_single_event():
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    params = {
        "apikey": os.getenv("TICKETMASTER_CONSUMER_KEY"),
        "countryCode": "FR",
        "size": 1  # On en veut UN seul
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "_embedded" in data:
        event = data["_embedded"]["events"][0]
        # On affiche le JSON de façon lisible
        print(json.dumps(event, indent=4, ensure_ascii=False))
        
        # --- PETIT GUIDE DE LECTURE ---
        print("\n--- 📝 GUIDE DE LECTURE DU FORMAT ---")
        print(f"Nom de l'event : {event.get('name')}")
        print(f"ID unique (clé primaire) : {event.get('id')}")
        print(f"Date locale : {event['dates']['start'].get('localDate')}")
        print(f"Lieu : {event['_embedded']['venues'][0]['name']} ({event['_embedded']['venues'][0]['city']['name']})")
        print(f"Catégorie : {event['classifications'][0]['segment']['name']}")
    else:
        print("Désolé, aucun événement trouvé même avec un filtre large.")

if __name__ == "__main__":
    inspect_single_event()