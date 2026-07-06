"""Router FastAPI per Segnalazione. Porting 1:1 di segnalazioneRouter.js."""

from typing import Optional

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query

from src.dao import segnalazione_dao
from src.database import get_connection
from src.schemas.segnalazione import SegnalazioneCreate, StatoSegnalazioneUpdate

router = APIRouter(tags=["Segnalazioni"])


@router.post("/segnalazioni", status_code=201)
async def create_segnalazione(
    segnalazione: SegnalazioneCreate,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """Crea segnalazione. Porting di POST /segnalazioni."""
    async with conn.transaction():
        result = await segnalazione_dao.create_segnalazione(
            conn, segnalazione.model_dump()
        )
        if not result:
            raise HTTPException(
                status_code=400, detail="Creazione segnalazione fallita"
            )
        return result


@router.get("/segnalazioni")
async def get_segnalazioni(
    conn: asyncpg.Connection = Depends(get_connection),
    stato: Optional[str] = Query(None),
    id_segnalante: Optional[int] = Query(None),
):
    """Elenco segnalazioni con filtri. Porting di GET /segnalazioni."""
    async with conn.transaction():
        filtri: dict = {}
        if stato:
            filtri["stato"] = stato
        if id_segnalante is not None:
            filtri["id_segnalante"] = id_segnalante
        return await segnalazione_dao.find_segnalazioni(conn, filtri)


# PRIMA di /{id}
@router.put("/segnalazioni/{id}/stato")
async def update_stato_segnalazione(
    id: int,
    body: StatoSegnalazioneUpdate,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """Aggiorna stato segnalazione. Porting di PUT /segnalazioni/:id/stato."""
    async with conn.transaction():
        result = await segnalazione_dao.update_segnalazione_stato(conn, id, body.stato)
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Segnalazione non trovata o stato non aggiornato",
            )
        return {"messaggio": "Stato segnalazione aggiornato con successo"}


@router.get("/segnalazioni/{id}")
async def get_segnalazione(id: int, conn: asyncpg.Connection = Depends(get_connection)):
    """Dettaglio segnalazione. Porting di GET /segnalazioni/:id."""
    async with conn.transaction():
        seg = await segnalazione_dao.find_segnalazione_by_id(conn, id)
        if not seg or not seg.get("id"):
            raise HTTPException(status_code=404, detail="Segnalazione non trovata")
        return seg
