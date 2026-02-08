# clean_functions.py

def normalize_name(nom: str, prenom: str = "") -> str:
    """Combine, nettoie et met en minuscule pour une recherche fiable."""
    p = prenom.strip() if prenom else ""
    n = nom.strip() if nom else ""

    full = f"{n} {p}".strip().lower()
    return " ".join(full.split())