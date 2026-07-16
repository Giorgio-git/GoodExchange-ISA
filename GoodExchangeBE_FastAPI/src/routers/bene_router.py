"""
Router FastAPI per l'entità Bene.
Porting 1:1 di GoodExchangeBE/routes/beneRouter.js in Python/FastAPI.

Gestione BYTEA:
- POST /beni/:id/immagine: riceve un UploadFile e salva i bytes
- GET /beni/:id/immagine: restituisce i bytes come Response con media_type
- DELETE /beni/:id/immagine: azzera il campo immagine a NULL
"""

import logging
from typing import Optional

import asyncpg
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response

from src.dao import bene_dao, utente_dao
from src.database import get_connection
from src.schemas.bene import BeneCreate, BeneUpdate
from src.services import bene_service

router = APIRouter(tags=["Beni"])
logger = logging.getLogger(__name__)


# ——— GET /api/beni ———
@router.get("/beni")
async def get_beni(
    conn: asyncpg.Connection = Depends(get_connection),
    id_proprietario: Optional[int] = Query(None),
    id_categoria: Optional[int] = Query(None),
    stato: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    limit: Optional[int] = Query(None),
    citta: Optional[str] = Query(None),
    regione: Optional[str] = Query(None),
    provincia: Optional[str] = Query(None),
    via: Optional[str] = Query(None),
    civico: Optional[str] = Query(None),
):
    """
    Elenco beni con filtri dinamici.
    Se filtrati per citta/regione/provincia/via/civico, esegue prima la ricerca degli utenti della zona.
    Porting di GET /beni in beneRouter.js.
    """
    async with conn.transaction():
        # Filtro per zona: prima trova gli utenti, poi i loro beni
        if citta or regione or provincia or via or civico:
            filtri_utente: dict = {}
            if citta:
                filtri_utente["citta"] = citta
            if regione:
                filtri_utente["regione"] = regione
            if provincia:
                filtri_utente["provincia"] = provincia
            if via:
                filtri_utente["via"] = via
            if civico:
                filtri_utente["civico"] = civico

            utenti = await utente_dao.find_utenti(conn, filtri_utente)
            if not utenti:
                return []
            id_proprietari = [u["id"] for u in utenti]
            stato_filtro = (
                stato
                if id_proprietario is not None
                else (True if stato is None else stato)
            )
            return await bene_dao.find_beni_by_proprietari(
                conn, id_proprietari, stato=stato_filtro
            )

        # Filtro standard
        filters: dict = {}
        if id_proprietario is None and stato is None:
            filters["stato"] = True
        elif stato is not None:
            filters["stato"] = stato
        if id_proprietario is not None:
            filters["id_proprietario"] = id_proprietario
        if id_categoria is not None:
            filters["id_categoria"] = id_categoria
        if search:
            filters["search"] = search
        if sort:
            filters["sort"] = sort
        if limit:
            filters["limit"] = limit

        return await bene_dao.find_beni(conn, filters)


# ——— POST /api/beni ———
@router.post("/beni", status_code=201)
async def create_bene(
    bene: BeneCreate,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """
    Crea un nuovo bene e aggiorna i crediti_valore_beni del proprietario.
    Delega al bene_service per la logica di aggiornamento crediti
    (Architettura Three-Tier).
    """
    async with conn.transaction():
        result = await bene_service.crea_bene_con_crediti(conn, bene.model_dump())
        if not result:
            raise HTTPException(status_code=400, detail="Creazione bene fallita")
        return result


# ——— POST /api/beni/:id/immagine — PRIMA di /{id} ———
@router.post("/beni/{id}/immagine", status_code=201)
async def upload_immagine(
    id: int,
    file: UploadFile = File(...),
    conn: asyncpg.Connection = Depends(get_connection),
):
    """
    Upload immagine bene come BYTEA nel database.
    Porting di POST /beni/:id/immagine con multer in beneRouter.js.
    """
    async with conn.transaction():
        file_bytes = await file.read()
        await bene_dao.update_bene_immagine(conn, id, file_bytes)
        return {"messaggio": "Immagine caricata con successo"}


# ——— GET /api/beni/:id/immagine — PRIMA di /{id} ———
@router.get("/beni/{id}/immagine")
async def get_immagine(
    id: int,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """
    Restituisce l'immagine del bene come bytes con media_type image/jpeg.
    Porting di GET /beni/:id/immagine in beneRouter.js.
    """
    async with conn.transaction():
        img = await bene_dao.get_bene_immagine(conn, id)
        if img is None:
            raise HTTPException(status_code=404, detail="Immagine non trovata")
        return Response(content=img, media_type="image/jpeg")


# ——— DELETE /api/beni/:id/immagine — PRIMA di /{id} ———
@router.delete("/beni/{id}/immagine")
async def delete_immagine(
    id: int,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """
    Elimina (azzera) l'immagine di un bene.
    Porting di DELETE /beni/:id/immagine in beneRouter.js.
    """
    async with conn.transaction():
        await bene_dao.delete_bene_immagine(conn, id)
        return {"messaggio": "Immagine eliminata con successo"}


# ——— PUT /api/beni/:id/blocca — PRIMA di /{id} ———
@router.put("/beni/{id}/blocca")
async def blocca_bene(
    id: int,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """Blocca un bene (stato=False) e ricalcola i crediti. Porting di PUT /beni/:id/blocca."""
    async with conn.transaction():
        result = await bene_service.blocca_bene_con_crediti(conn, id)
        if not result:
            raise HTTPException(status_code=404, detail="Bene non trovato")
        return {"messaggio": "Bene bloccato con successo"}


# ——— PUT /api/beni/:id/sblocca — PRIMA di /{id} ———
@router.put("/beni/{id}/sblocca")
async def sblocca_bene(
    id: int,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """Sblocca un bene (stato=True) e ricalcola i crediti. Porting di PUT /beni/:id/sblocca."""
    async with conn.transaction():
        result = await bene_service.sblocca_bene_con_crediti(conn, id)
        if not result:
            raise HTTPException(status_code=404, detail="Bene non trovato")
        return {"messaggio": "Bene sbloccato con successo"}


# ——— GET /api/beni/:id ———
@router.get("/beni/{id}")
async def get_bene(
    id: int,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """
    Recupera un bene per ID.
    Porting di GET /beni/:id in beneRouter.js.
    """
    async with conn.transaction():
        bene = await bene_dao.find_bene_by_id(conn, id)
        if not bene:
            raise HTTPException(status_code=404, detail="Bene non trovato")
        return bene


# ——— PUT /api/beni/:id ———
@router.put("/beni/{id}")
async def update_bene(
    id: int,
    aggiornamenti: BeneUpdate,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """
    Aggiorna un bene.
    Porting di PUT /beni/:id in beneRouter.js.
    """
    async with conn.transaction():
        # Filtra i campi None
        data = {k: v for k, v in aggiornamenti.model_dump().items() if v is not None}
        result = await bene_service.aggiorna_bene_con_crediti(conn, id, data)
        if not result:
            raise HTTPException(
                status_code=404, detail="Bene non trovato o non aggiornato"
            )
        return {"messaggio": "Bene aggiornato con successo"}


# ——— DELETE /api/beni/:id ———
@router.delete("/beni/{id}")
async def delete_bene(
    id: int,
    id_proprietario: int = Query(..., description="ID del proprietario del bene"),
    conn: asyncpg.Connection = Depends(get_connection),
):
    """
    Elimina un bene e ricalcola i crediti_valore_beni del proprietario.
    Delega al bene_service per la logica di ricalcolo crediti
    (Architettura Three-Tier).
    """
    async with conn.transaction():
        result = await bene_service.elimina_bene_con_crediti(conn, id, id_proprietario)
        if not result:
            raise HTTPException(status_code=404, detail="Bene non trovato")
        return {"messaggio": "Bene eliminato con successo"}
