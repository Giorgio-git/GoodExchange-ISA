"""
DAO per Preferiti.
"""

import logging
from typing import Optional

import asyncpg

from src.dao.utente_dao import _rows_affected

logger = logging.getLogger(__name__)


async def find_preferiti_by_utente(
    conn: asyncpg.Connection, id_utente: int
) -> Optional[dict]:
    """Recupera la lista preferiti di un utente."""
    try:
        sql = "SELECT * FROM preferiti WHERE id_utente=$1"
        row = await conn.fetchrow(sql, id_utente)
        return dict(row) if row else None
    except Exception as err:
        logger.error("Errore in find_preferiti_by_utente: %s", err)
        raise


async def create_preferiti(
    conn: asyncpg.Connection, id_utente: int, id_preferiti: Optional[int]
) -> bool:
    """Crea una lista preferiti per un utente."""
    try:
        sql = "INSERT INTO preferiti (id_utente) VALUES ($1) RETURNING id"
        row = await conn.fetchrow(sql, id_utente)
        return row is not None
    except Exception as err:
        logger.error("Errore in create_preferiti: %s", err)
        raise


async def delete_preferiti(conn: asyncpg.Connection, id_utente: int) -> bool:
    """Elimina la lista preferiti di un utente."""
    try:
        sql = "DELETE FROM preferiti WHERE id_utente=$1"
        status = await conn.execute(sql, id_utente)
        return _rows_affected(status) > 0
    except Exception as err:
        logger.error("Errore in delete_preferiti: %s", err)
        raise
