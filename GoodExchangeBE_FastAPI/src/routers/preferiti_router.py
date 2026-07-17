"""Router FastAPI per Preferiti."""

import asyncpg
from fastapi import APIRouter, Depends, HTTPException

from src.dao import preferiti_dao
from src.database import get_connection

router = APIRouter(tags=["Preferiti"])


@router.get("/preferiti/{id_utente}")
async def get_preferiti(
    id_utente: int, conn: asyncpg.Connection = Depends(get_connection)
):
    """Lista preferiti utente."""
    async with conn.transaction():
        pref = await preferiti_dao.find_preferiti_by_utente(conn, id_utente)
        if not pref:
            # Lazy Creation: se l'utente non ha ancora un contenitore preferiti (es. appena registrato),
            # lo creiamo automaticamente su richiesta
            await preferiti_dao.create_preferiti(conn, id_utente, None)
            pref = await preferiti_dao.find_preferiti_by_utente(conn, id_utente)
            if not pref:
                raise HTTPException(
                    status_code=404, detail="Lista preferiti non trovata"
                )
        return pref


@router.post("/preferiti/{id_utente}", status_code=201)
async def create_preferiti(
    id_utente: int,
    body: dict,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """Crea lista preferiti."""
    async with conn.transaction():
        result = await preferiti_dao.create_preferiti(
            conn, id_utente, body.get("id_preferiti")
        )
        if not result:
            raise HTTPException(
                status_code=400, detail="Creazione lista preferiti fallita"
            )
        return {"messaggio": "Lista preferiti creata"}


@router.delete("/preferiti/{id_utente}")
async def delete_preferiti(
    id_utente: int, conn: asyncpg.Connection = Depends(get_connection)
):
    """Elimina lista preferiti."""
    async with conn.transaction():
        result = await preferiti_dao.delete_preferiti(conn, id_utente)
        if not result:
            raise HTTPException(
                status_code=404, detail="Lista preferiti non trovata o non eliminata"
            )
        return {"messaggio": "Lista preferiti eliminata"}
