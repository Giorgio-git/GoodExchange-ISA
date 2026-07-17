"""
DAO per l'entità Categoria.
"""

import logging
from typing import Optional

import asyncpg

from src.dao.utente_dao import _rows_affected

logger = logging.getLogger(__name__)


async def find_categorie(conn: asyncpg.Connection) -> list[dict]:
    """Restituisce tutte le categorie ordinate per nome."""
    try:
        sql = "SELECT * FROM categoria ORDER BY nome ASC"
        rows = await conn.fetch(sql)
        return [dict(r) for r in rows]
    except Exception as err:
        logger.error("Errore in find_categorie: %s", err)
        raise


async def find_categoria_by_id(
    conn: asyncpg.Connection, id_categoria: int
) -> Optional[dict]:
    """Recupera una categoria per ID."""
    try:
        sql = "SELECT * FROM categoria WHERE id=$1"
        row = await conn.fetchrow(sql, id_categoria)
        return dict(row) if row else None
    except Exception as err:
        logger.error("Errore in find_categoria_by_id: %s", err)
        raise


async def create_categoria(conn: asyncpg.Connection, categoria: dict) -> Optional[dict]:
    """Crea una nuova categoria."""
    try:
        sql = """
            INSERT INTO categoria (nome, crediti, descrizione)
            VALUES ($1, $2, $3)
            RETURNING id
        """
        row = await conn.fetchrow(
            sql,
            categoria["nome"],
            categoria.get("crediti", 0),
            categoria.get("descrizione"),
        )
        if row is None:
            return None
        return {**categoria, "id": row["id"]}
    except Exception as err:
        logger.error("Errore in create_categoria: %s", err)
        raise


async def update_categoria(
    conn: asyncpg.Connection, id_categoria: int, aggiornamenti: dict
) -> bool:
    """Aggiornamento dinamico di una categoria."""
    try:
        parts: list[str] = []
        params: list = []

        for campo, valore in aggiornamenti.items():
            if valore is None and campo != "descrizione":
                continue
            parts.append(f"{campo} = ${len(params) + 1}")
            params.append(valore)

        if not parts:
            return False

        sql = "UPDATE categoria SET " + ", ".join(parts)
        sql += f" WHERE id = ${len(params) + 1}"
        params.append(id_categoria)

        status = await conn.execute(sql, *params)
        return _rows_affected(status) > 0
    except Exception as err:
        logger.error("Errore in update_categoria: %s", err)
        raise


async def delete_categoria(conn: asyncpg.Connection, id_categoria: int) -> bool:
    """Elimina una categoria per ID."""
    try:
        sql = "DELETE FROM categoria WHERE id = $1"
        status = await conn.execute(sql, id_categoria)
        return _rows_affected(status) > 0
    except Exception as err:
        logger.error("Errore in delete_categoria: %s", err)
        raise
