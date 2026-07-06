"""Router FastAPI per Recensione. Porting 1:1 di recensioneRouter.js."""

from typing import Optional

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query

from src.dao import recensione_dao
from src.database import get_connection
from src.schemas.recensione import RecensioneCreate

router = APIRouter(tags=["Recensioni"])


@router.get("/recensioni")
async def get_recensioni(
    conn: asyncpg.Connection = Depends(get_connection),
    id_bene: Optional[int] = Query(None),
    id_beneficiario: Optional[int] = Query(None),
):
    """Elenco recensioni con filtri. Porting di GET /recensioni."""
    async with conn.transaction():
        filtri: dict = {}
        if id_bene is not None:
            filtri["id_bene"] = id_bene
        if id_beneficiario is not None:
            filtri["id_beneficiario"] = id_beneficiario
        return await recensione_dao.find_recensioni(conn, filtri)


@router.get("/recensioni/{id}")
async def get_recensione(id: int, conn: asyncpg.Connection = Depends(get_connection)):
    """Dettaglio recensione. Porting di GET /recensioni/:id."""
    async with conn.transaction():
        rec = await recensione_dao.find_recensione_by_id(conn, id)
        if not rec or not rec.get("id"):
            raise HTTPException(status_code=404, detail="Recensione non trovata")
        return rec


@router.post("/recensioni", status_code=201)
async def create_recensione(
    recensione: RecensioneCreate,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """Crea recensione. Porting di POST /recensioni."""
    async with conn.transaction():
        result = await recensione_dao.create_recensione(conn, recensione.model_dump())
        if not result:
            raise HTTPException(status_code=400, detail="Creazione recensione fallita")
        return result


@router.put("/recensioni/{id}")
async def update_recensione(
    id: int,
    body: dict,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """Aggiorna recensione. Porting di PUT /recensioni/:id."""
    async with conn.transaction():
        result = await recensione_dao.update_recensione(conn, id, body)
        if not result:
            raise HTTPException(
                status_code=404, detail="Recensione non trovata o non aggiornata"
            )
        return {"messaggio": "Recensione aggiornata con successo"}


@router.delete("/recensioni/{id}")
async def delete_recensione(
    id: int, conn: asyncpg.Connection = Depends(get_connection)
):
    """Elimina recensione. Porting di DELETE /recensioni/:id."""
    async with conn.transaction():
        result = await recensione_dao.delete_recensione(conn, id)
        if not result:
            raise HTTPException(
                status_code=404, detail="Recensione non trovata o non eliminata"
            )
        return {"messaggio": "Recensione eliminata con successo"}
