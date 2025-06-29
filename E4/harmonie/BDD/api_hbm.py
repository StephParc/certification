# api_hbm.py
from fastapi import FastAPI
from routes import evenements, users, authentication, associations, auteurs, partitions, partitions_hbm

app = FastAPI()

app.include_router(authentication.router)
app.include_router(users.router)
app.include_router(auteurs.router)
app.include_router(evenements.router)
app.include_router(partitions.router)
app.include_router(partitions_hbm.router)
app.include_router(associations.router)

