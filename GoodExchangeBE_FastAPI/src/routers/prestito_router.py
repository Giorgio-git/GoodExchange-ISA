"""
Router FastAPI per l'entità Prestito.

ORDINE CRITICO DELLE ROUTE:
FastAPI fa matching in ordine di registrazione. Le route statiche
(/filtri, /disponibilita/:id, /calendario/:id) devono precedere /{id}.

ARCHITETTURA:
La logica transazionale complessa (Strict 2PL, FSM) è delegata al
prestito_service per separare la presentazione dalla business logic.
"""

import logging
from datetime import date
from typing import Optional

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query

from src.dao import prestito_dao
from src.database import get_connection
from src.schemas.prestito import PrestitoCreate, StatoPrestitoUpdate
from src.services import prestito_service

router = APIRouter(tags=["Prestiti"])
logger = logging.getLogger(__name__)


# ——— GET /api/prestiti/filtri — PRIMA di /{id} ———
@router.get("/prestiti/filtri")
async def get_prestiti_filtrati(
    conn: asyncpg.Connection = Depends(get_connection),
    id_bene: Optional[int] = Query(None),
    id_beneficiario: Optional[int] = Query(None),
    id_proprietario: Optional[int] = Query(None),
    stato: Optional[str] = Query(None),
    data_da: Optional[date] = Query(None),
    data_a: Optional[date] = Query(None),
):
    """
    Elenco prestiti con filtri avanzati.
    """
    async with conn.transaction():
        filtri: dict = {}
        if id_bene is not None:
            filtri["id_bene"] = id_bene
        if id_beneficiario is not None:
            filtri["id_beneficiario"] = id_beneficiario
        if id_proprietario is not None:
            filtri["id_proprietario"] = id_proprietario
        if stato:
            filtri["stato"] = stato
        if data_da:
            filtri["data_da"] = data_da
        if data_a:
            filtri["data_a"] = data_a

        return await prestito_dao.find_prestiti(conn, filtri)


# ——— GET /api/prestiti ———
@router.get("/prestiti")
async def get_prestiti(
    conn: asyncpg.Connection = Depends(get_connection),
    id_bene: Optional[int] = Query(None),
    id_beneficiario: Optional[int] = Query(None),
    id_proprietario: Optional[int] = Query(None),
    stato: Optional[str] = Query(None),
):
    """
    Elenco prestiti base.
    """
    async with conn.transaction():
        filtri: dict = {}
        if id_bene is not None:
            filtri["id_bene"] = id_bene
        if id_beneficiario is not None:
            filtri["id_beneficiario"] = id_beneficiario
        if id_proprietario is not None:
            filtri["id_proprietario"] = id_proprietario
        if stato:
            filtri["stato"] = stato

        return await prestito_dao.find_prestiti(conn, filtri)


# ——— GET /api/prestiti/disponibilita/:bene_id — PRIMA di /{id} ———
@router.get("/prestiti/disponibilita/{bene_id}")
async def verifica_disponibilita(
    bene_id: int,
    data_inizio: date = Query(...),
    data_fine: date = Query(...),
    conn: asyncpg.Connection = Depends(get_connection),
):
    """
    Verifica disponibilità di un bene in un periodo.
    """
    async with conn.transaction():
        disponibile = await prestito_dao.verifica_disponibilita(
            conn, bene_id, data_inizio, data_fine
        )
        return {"disponibile": disponibile}


# ——— GET /api/prestiti/calendario/:bene_id — PRIMA di /{id} ———
@router.get("/prestiti/calendario/{bene_id}")
async def get_calendario(
    bene_id: int,
    anno: int = Query(...),
    mese: int = Query(...),
    conn: asyncpg.Connection = Depends(get_connection),
):
    """
    Calendario dei prestiti per un bene in un mese specifico.
    """
    async with conn.transaction():
        return await prestito_dao.get_calendario_bene(conn, bene_id, anno, mese)


# ——— GET /api/prestiti/:id ———
@router.get("/prestiti/{id}")
async def get_prestito(
    id: int,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """
    Recupera un prestito per ID.
    """
    async with conn.transaction():
        prestito = await prestito_dao.find_prestito_by_id(conn, id)
        if not prestito:
            raise HTTPException(status_code=404, detail="Prestito non trovato")
        return prestito


# ——— POST /api/prestiti ———
@router.post("/prestiti", status_code=201)
async def create_prestito(
    prestito: PrestitoCreate,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """
    Crea un nuovo prestito dopo verifica disponibilità.
    Delega al service layer per la logica transazionale.
    """
    try:
        async with conn.transaction():
            result = await prestito_service.crea_prestito(
                conn,
                prestito.id_bene,
                prestito.id_beneficiario,
                prestito.id_proprietario,
                prestito.data_inizio,
                prestito.data_fine,
            )
        return result
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


# ——— PUT /api/prestiti/:id/stato ———
@router.put("/prestiti/{id}/stato")
async def update_stato_prestito(
    id: int,
    body: StatoPrestitoUpdate,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """
    Aggiorna lo stato di un prestito rispettando la FSM.
    Implementa Strict 2PL tramite SELECT ... FOR UPDATE nel service layer.
    """
    try:
        async with conn.transaction():
            result = await prestito_service.aggiorna_stato_prestito(
                conn, id, body.stato
            )
        return result
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


# ——— DELETE /api/prestiti/:id ———
@router.delete("/prestiti/{id}")
async def delete_prestito(
    id: int,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """
    Elimina un prestito per ID.
    """
    async with conn.transaction():
        result = await prestito_dao.delete_prestito(conn, id)
        if not result:
            raise HTTPException(status_code=404, detail="Prestito non trovato")
        return {"messaggio": "Prestito eliminato con successo"}
