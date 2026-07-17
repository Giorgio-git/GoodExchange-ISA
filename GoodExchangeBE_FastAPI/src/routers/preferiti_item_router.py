"""Router FastAPI per PreferitiItem."""

import asyncpg
from fastapi import APIRouter, Depends, HTTPException

from src.dao import preferiti_item_dao
from src.database import get_connection

router = APIRouter(tags=["PreferitiItem"])


@router.get("/preferitiItem/{id_preferiti}")
async def get_utenti_preferiti(
    id_preferiti: int, conn: asyncpg.Connection = Depends(get_connection)
):
    """Utenti preferiti di una lista."""
    async with conn.transaction():
        return await preferiti_item_dao.get_utenti_preferiti(conn, id_preferiti)


@router.post("/preferitiItem/{id_preferiti}/{id_utente_preferito}", status_code=201)
async def add_utente_preferito(
    id_preferiti: int,
    id_utente_preferito: int,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """Aggiungi utente preferito."""
    async with conn.transaction():
        result = await preferiti_item_dao.add_utente_preferito(
            conn, id_preferiti, id_utente_preferito
        )
        if not result:
            raise HTTPException(
                status_code=400, detail="Aggiunta utente preferito fallita"
            )
        return {"messaggio": "Utente preferito aggiunto"}


@router.delete("/preferitiItem/{id_preferiti}/{id_utente_preferito}")
async def remove_utente_preferito(
    id_preferiti: int,
    id_utente_preferito: int,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """Rimuovi utente preferito."""
    async with conn.transaction():
        result = await preferiti_item_dao.remove_utente_preferito(
            conn, id_preferiti, id_utente_preferito
        )
        if not result:
            raise HTTPException(
                status_code=404, detail="Utente preferito non trovato o non rimosso"
            )
        return {"messaggio": "Utente preferito rimosso"}
