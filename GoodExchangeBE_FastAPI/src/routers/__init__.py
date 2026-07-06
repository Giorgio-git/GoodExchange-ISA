"""
Package dei router FastAPI.
Esporta tutti i moduli router per l'importazione in main.py.
"""

from src.routers import (
    bene_router,
    categoria_router,
    feedback_router,
    messaggio_router,
    preferiti_item_router,
    preferiti_router,
    prestito_router,
    recensione_router,
    segnalazione_router,
    suggerimento_router,
    utente_router,
)

__all__ = [
    "utente_router",
    "bene_router",
    "prestito_router",
    "categoria_router",
    "feedback_router",
    "messaggio_router",
    "recensione_router",
    "segnalazione_router",
    "suggerimento_router",
    "preferiti_router",
    "preferiti_item_router",
]
