# api_hbm.py
from fastapi import FastAPI
from E4.harmonie.BDD.routes import evenements, users, authentication, associations, auteurs, partitions, partitions_hbm, instruments
from E4.harmonie.BDD.routes import instruments_dico, musiciens, partitions_details, regles_substitution

app = FastAPI(title="HBM - Harmonie Manager 2026")

app.include_router(authentication.router)
app.include_router(users.router)
app.include_router(auteurs.router)
app.include_router(evenements.router)
app.include_router(partitions.router)
app.include_router(partitions_hbm.router)
app.include_router(associations.router)
app.include_router(instruments.router)
# app.include_router(instruments_dico.router)
app.include_router(musiciens.router)
# app.include_router(partitions_details.router)
# app.include_router(regles_substitution.router)

@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API HBM"}
