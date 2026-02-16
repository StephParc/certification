import requests
import json
import os

# Remplace par ta clé ou assure-toi qu'elle est en variable d'env
API_KEY = "d7ad768222444707a1f5ae229c43b357"
AGENDA_UID = "30166879"

def test_agenda_content(uid):
    # 1. Tester l'existence de l'agenda
    meta_url = f"https://api.openagenda.com/v2/agendas/{uid}?key={API_KEY}"
    
    # 2. Chercher les 2 premiers événements pour voir la structure
    events_url = f"https://api.openagenda.com/v2/agendas/{uid}/events?key={API_KEY}&limit=2"

    print(f"--- Vérification de l'Agenda {uid} ---")
    
    try:
        # Check Meta
        meta_res = requests.get(meta_url)
        if meta_res.status_code == 200:
            print(f"Titre : {meta_res.json().get('title')}")
        else:
            print(f"Erreur Meta: {meta_res.status_code}")

        # Check Events
        events_res = requests.get(events_url)
        if events_res.status_code == 200:
            data = events_res.json()
            events = data.get('events', [])
            
            if not events:
                print("⚠️ L'agenda est vide ou n'a pas d'événements publics.")
                return

            print(f"✅ {len(events)} événement(s) trouvé(s).")
            
            # On inspecte le premier événement
            first = events[0]
            print("\n--- Structure du premier événement ---")
            print(f"Titre: {first.get('title', {}).get('fr')}")
            print(f"Lieu: {first.get('location', {}).get('name')} ({first.get('location', {}).get('city')})")
            
            # Vérification des Timings (Crucial pour dbt)
            timings = first.get('timings', [])
            print(f"Nombre de dates prévues: {len(timings)}")
            if timings:
                print(f"Exemple de timing: {timings[0].get('start')} -> {timings[0].get('end')}")

            # Vérification des Tags/Catégories
            print(f"JSON complet du premier événement (extrait) :\n{json.dumps(first, indent=2)[:500]}...")

        else:
            print(f"Erreur Events: {events_res.status_code} - {events_res.text}")

    except Exception as e:
        print(f"Erreur lors du test : {e}")

if __name__ == "__main__":
    test_agenda_content(AGENDA_UID)