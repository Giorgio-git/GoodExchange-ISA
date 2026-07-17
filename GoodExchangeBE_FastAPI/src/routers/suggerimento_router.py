"""
Router FastAPI per Suggerimento.
ORDINE: /utente/:id PRIMA di /:id e PUT /:id/stato.
"""

from typing import Optional

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query

from src.dao import suggerimento_dao
from src.database import get_connection
from src.schemas.suggerimento import StatoSuggerimentoUpdate, SuggerimentoCreate

router = APIRouter(tags=["Suggerimenti"])


# PRIMA di /{id}: PUT con sub-path
@router.put("/suggerimenti/{id}/stato")
async def update_stato_suggerimento(
    id: int,
    body: StatoSuggerimentoUpdate,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """Aggiorna stato suggerimento."""
    async with conn.transaction():
        ok = await suggerimento_dao.update_suggerimento_stato(conn, id, body.stato)
        if not ok:
            raise HTTPException(status_code=404, detail="Suggerimento non trovato")
        return {"success": True, "stato": body.stato}


@router.get("/suggerimenti")
async def get_suggerimenti(
    conn: asyncpg.Connection = Depends(get_connection),
    id_mittente: Optional[int] = Query(None),
    stato: Optional[str] = Query(None),
):
    """Elenco suggerimenti con filtri."""
    filtri: dict = {}
    if id_mittente is not None:
        filtri["id_mittente"] = id_mittente
    if stato:
        filtri["stato"] = stato
    return await suggerimento_dao.find_suggerimenti(conn, filtri)


@router.post("/suggerimenti", status_code=201)
async def create_suggerimento(
    body: SuggerimentoCreate,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """Crea suggerimento."""
    async with conn.transaction():
        if not body.id_mittente:
            raise HTTPException(status_code=400, detail="id_mittente richiesto")
        nuovo = await suggerimento_dao.create_suggerimento(conn, body.model_dump())
        return nuovo


# PRIMA di /{id}
@router.get("/suggerimenti/utente/{id}")
async def get_suggerimenti_utente(
    id: int, conn: asyncpg.Connection = Depends(get_connection)
):
    """Suggerimenti per utente."""
    return await suggerimento_dao.find_suggerimenti(conn, {"id_mittente": id})
