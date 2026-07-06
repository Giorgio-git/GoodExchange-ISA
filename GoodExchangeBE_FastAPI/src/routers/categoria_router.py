"""Router FastAPI per Categoria. Porting 1:1 di categoriaRouter.js."""

import asyncpg
from fastapi import APIRouter, Depends, HTTPException

from src.dao import categoria_dao
from src.database import get_connection
from src.schemas.categoria import CategoriaCreate, CategoriaUpdate

router = APIRouter(tags=["Categorie"])


@router.get("/categorie")
async def get_categorie(conn: asyncpg.Connection = Depends(get_connection)):
    """Elenco categorie. Porting di GET /categorie."""
    async with conn.transaction():
        return await categoria_dao.find_categorie(conn)


@router.get("/categorie/{id}")
async def get_categoria(id: int, conn: asyncpg.Connection = Depends(get_connection)):
    """Dettaglio categoria. Porting di GET /categorie/:id."""
    async with conn.transaction():
        cat = await categoria_dao.find_categoria_by_id(conn, id)
        if not cat:
            raise HTTPException(status_code=404, detail="Categoria non trovata")
        return cat


@router.post("/categorie", status_code=201)
async def create_categoria(
    categoria: CategoriaCreate,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """Crea categoria. Porting di POST /categorie."""
    async with conn.transaction():
        result = await categoria_dao.create_categoria(conn, categoria.model_dump())
        if not result:
            raise HTTPException(status_code=400, detail="Creazione categoria fallita")
        return result


@router.put("/categorie/{id}")
async def update_categoria(
    id: int,
    aggiornamenti: CategoriaUpdate,
    conn: asyncpg.Connection = Depends(get_connection),
):
    """Aggiorna categoria. Porting di PUT /categorie/:id."""
    async with conn.transaction():
        data = {k: v for k, v in aggiornamenti.model_dump().items() if v is not None}
        result = await categoria_dao.update_categoria(conn, id, data)
        if not result:
            raise HTTPException(
                status_code=404, detail="Categoria non trovata o non aggiornata"
            )
        return {"messaggio": "Categoria aggiornata con successo"}


@router.delete("/categorie/{id}")
async def delete_categoria(id: int, conn: asyncpg.Connection = Depends(get_connection)):
    """Elimina categoria. Porting di DELETE /categorie/:id."""
    async with conn.transaction():
        result = await categoria_dao.delete_categoria(conn, id)
        if not result:
            raise HTTPException(
                status_code=404, detail="Categoria non trovata o non eliminata"
            )
        return {"messaggio": "Categoria eliminata con successo"}
