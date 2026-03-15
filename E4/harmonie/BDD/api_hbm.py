# api_hbm.py
"""
Main Application Entry Point - Harmonie Manager 2026.

This module initializes the FastAPI application and assembles all functional 
routers into a single API interface. It defines the global metadata and 
the root path for the service.

Architecture:
    - Modular Design: Each business domain (users, music, events) is 
      isolated in its own router for better maintainability.
    - Path Prefixing: The application is configured with a '/api' root_path 
      to facilitate deployment behind reverse proxies (Nginx/Traefik).
"""
from fastapi import FastAPI
from E4.harmonie.BDD.routes import (
    evenements, users, authentication, associations, 
    auteurs, partitions, partitions_hbm, instruments,
    instruments_dico, musiciens, partitions_details, regles_substitution
)

app = FastAPI(
    title="HBM - Harmonie Batterie Municipale",
    # root_path is essential for proper Swagger/OpenAPI documentation 
    # when running behind a proxy or in a sub-folder.
    root_path="/api"
)

# Inclusion of Security and Administrative Routers
app.include_router(authentication.router)
app.include_router(users.router)

# Inclusion of Core Business Routers
app.include_router(musiciens.router)
app.include_router(auteurs.router)
app.include_router(evenements.router)
app.include_router(partitions.router)
app.include_router(partitions_hbm.router)

# Inclusion of Hybrid and Advanced Logic Routers
app.include_router(partitions_details.router)
app.include_router(associations.router)
app.include_router(instruments.router)
app.include_router(instruments_dico.router)
app.include_router(regles_substitution.router)

