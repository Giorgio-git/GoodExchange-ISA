"""
Router FastAPI per l'entità Utente.

NOTA ORDINE ROUTE: Le route statiche (/login, /username/:username, /crediti)
devono essere registrate PRIMA delle route con parametri dinamici (/{id})
per evitare conflitti di matching in FastAPI.
"""

import logging
from typing import Optional

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query

from src.dao import utente_dao
from src.database import get_connection
from src.schemas.utente import (
    CauzioneUpdate,
    StatoUpdate,
    UtenteCreate,
    UtenteUpdate,
)
from src.services import utente_service

router = APIRouter(tags=["Utenti"])
logger = logging.getLogger(__name__)


# ——— POST /api/utenti/login ———
@router.post("/utenti/login")
async def login(
    body: dict,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """
    Autenticazione utente con username e password (in chiaro — da bcrypt in future iterazioni).
    """
    async with conn.transaction():
        utente = await utente_dao.find_utente_by_username(
            conn, body.get("username", "")
        )
        if not utente:
            raise HTTPException(status_code=401, detail="Credenziali non valide")
        if utente["password"] != body.get("password", ""):
            raise HTTPException(status_code=401, detail="Credenziali non valide")
        # Rimuovi la password dalla risposta
        result = {k: v for k, v in utente.items() if k != "password"}
        return {"messaggio": "Login effettuato con successo", "utente": result}


# ——— GET /api/utenti ———
@router.get("/utenti")
async def get_utenti(
    conn: asyncpg.Connection = Depends(get_connection),
    stato: Optional[str] = Query(None),
    ruolo: Optional[str] = Query(None),
    citta: Optional[str] = Query(None),
    regione: Optional[str] = Query(None),
):
    """
    Elenco utenti con filtri opzionali.
    """
    async with conn.transaction():
        filtri = {
            k: v
            for k, v in {
                "stato": stato,
                "ruolo": ruolo,
                "citta": citta,
                "regione": regione,
            }.items()
            if v is not None
        }
        utenti = await utente_dao.find_utenti(conn, filtri)
        # Rimuovi password dalla risposta
        return [{k: v for k, v in u.items() if k != "password"} for u in utenti]


# ——— GET /api/utenti/username/:username — PRIMA di /{id} ———
@router.get("/utenti/username/{username}")
async def get_utente_by_username(
    username: str,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """
    Recupera un utente per username.
    """
    async with conn.transaction():
        utente = await utente_dao.find_utente_by_username(conn, username)
        if not utente:
            raise HTTPException(status_code=404, detail="Utente non trovato")
        return {k: v for k, v in utente.items() if k != "password"}


# ——— GET /api/utenti/:id ———
@router.get("/utenti/{id}")
async def get_utente(
    id: int,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """
    Recupera un utente per ID.
    """
    async with conn.transaction():
        utente = await utente_dao.find_utente_by_id(conn, id)
        if not utente:
            raise HTTPException(status_code=404, detail="Utente non trovato")
        return {k: v for k, v in utente.items() if k != "password"}


# ——— GET /api/utenti/:id/crediti ———
@router.get("/utenti/{id}/crediti")
async def get_crediti_utente(
    id: int,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """
    Calcola e restituisce i crediti aggiornati di un utente.
    """
    async with conn.transaction():
        crediti_valore = await utente_dao.calcola_crediti_valore_beni(conn, id)
        crediti_accumulati = await utente_dao.calcola_crediti_accumulati(conn, id)
        return {
            "crediti_valore_beni": crediti_valore,
            "crediti_accumulati": crediti_accumulati,
        }


# ——— POST /api/utenti ———
@router.post("/utenti", status_code=201)
async def create_utente(
    utente: UtenteCreate,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """
    Crea un nuovo utente tramite service layer (registra_utente).
    """
    try:
        async with conn.transaction():
            result = await utente_service.registra_utente(conn, utente.model_dump())
            if not result:
                raise HTTPException(status_code=400, detail="Creazione utente fallita")
            return result
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(
            status_code=409, detail="Username o Codice Fiscale già registrato"
        ) from None


# ——— PUT /api/utenti/:id/stato ———
@router.put("/utenti/{id}/stato")
async def update_stato_utente(
    id: int,
    body: StatoUpdate,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """
    Aggiorna lo stato (attivo/disattivo) di un utente.
    """
    async with conn.transaction():
        result = await utente_dao.update_utente_stato(conn, id, body.stato)
        if not result:
            raise HTTPException(status_code=404, detail="Utente non trovato")
        return {"messaggio": "Stato utente aggiornato con successo"}


# ——— PUT /api/utenti/:id/cauzione ———
@router.put("/utenti/{id}/cauzione")
async def update_cauzione_utente(
    id: int,
    body: CauzioneUpdate,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """
    Aggiorna la cauzione di un utente.
    """
    async with conn.transaction():
        result = await utente_dao.update_utente_cauzione(conn, id, body.cauzione)
        if not result:
            raise HTTPException(status_code=404, detail="Utente non trovato")
        return {"messaggio": "Cauzione aggiornata con successo"}


# ——— PUT /api/utenti/:id ———
@router.put("/utenti/{id}")
async def update_utente(
    id: int,
    body: UtenteUpdate,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """
    Aggiornamento dinamico di un utente.
    """
    async with conn.transaction():
        esistente = await utente_dao.find_utente_by_id(conn, id)
        if not esistente:
            raise HTTPException(status_code=404, detail="Utente non trovato")
        dati = body.model_dump(exclude_unset=True)
        await utente_dao.update_utente(conn, id, dati)
        return {"messaggio": "Utente aggiornato con successo"}
