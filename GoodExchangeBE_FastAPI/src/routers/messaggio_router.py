"""
Router FastAPI per Messaggio.
ORDINE: /destinatario/:id, /mittente/:id, /tipo/:tipo PRIMA di /:id.
"""

from typing import Optional

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query

from src.dao import messaggio_dao
from src.database import get_connection
from src.schemas.messaggio import MessaggioCreate

router = APIRouter(tags=["Messaggi"])


@router.post("/messaggi", status_code=201)
async def create_messaggio(
    messaggio: MessaggioCreate,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """Crea messaggio."""
    new_id = await messaggio_dao.create_messaggio(conn, messaggio.model_dump())
    return {"id": new_id}


# PRIMA di /{id}
@router.get("/messaggi/destinatario/{id}")
async def get_messaggi_by_destinatario(
    id: int, conn: asyncpg.Connection = Depends(get_connection)
):
    """Messaggi per destinatario."""
    return await messaggio_dao.find_messaggi_by_destinatario(conn, id)


# PRIMA di /{id}
@router.get("/messaggi/mittente/{id}")
async def get_messaggi_by_mittente(
    id: int, conn: asyncpg.Connection = Depends(get_connection)
):
    """Messaggi per mittente."""
    return await messaggio_dao.find_messaggi_by_mittente(conn, id)


# PRIMA di /{id}
@router.get("/messaggi/tipo/{tipo}")
async def get_messaggi_by_tipo(
    tipo: str,
    conn: asyncpg.Connection = Depends(get_connection),
    id_riferito: Optional[int] = Query(None),
):
    """Messaggi per tipo (e opzionalmente id_riferito)."""
    if id_riferito is not None:
        return await messaggio_dao.find_messaggi_by_tipo_and_riferito(
            conn, tipo, id_riferito
        )
    return await messaggio_dao.find_messaggi_by_tipo(conn, tipo)


@router.get("/messaggi/{id}")
async def get_messaggio(id: int, conn: asyncpg.Connection = Depends(get_connection)):
    """Messaggio per ID."""
    msg = await messaggio_dao.find_messaggio_by_id(conn, id)
    if not msg:
        raise HTTPException(status_code=404, detail="Messaggio non trovato")
    return msg


@router.put("/messaggi/{id}")
async def update_messaggio(
    id: int,
    body: dict,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """Aggiorna messaggio."""
    await messaggio_dao.update_messaggio(conn, id, body)
    return {"success": True}


@router.delete("/messaggi/{id}")
async def delete_messaggio(id: int, conn: asyncpg.Connection = Depends(get_connection)):
    """Elimina messaggio."""
    await messaggio_dao.delete_messaggio(conn, id)
    return {"success": True}
