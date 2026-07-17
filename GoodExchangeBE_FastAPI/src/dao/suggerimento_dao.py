"""
DAO per Suggerimento.
"""

import logging
from typing import Optional

import asyncpg

from src.dao.utente_dao import _rows_affected

logger = logging.getLogger(__name__)


async def find_suggerimenti(conn: asyncpg.Connection, filtri: dict) -> list[dict]:
    """Restituisce una lista filtrata di suggerimenti."""
    try:
        sql = "SELECT * FROM suggerimento"
        params: list = []
        parts: list[str] = []

        for campo, valore in filtri.items():
            if valore is None or valore == "":
                continue
            parts.append(f"{campo} = ${len(params) + 1}")
            params.append(valore)

        if parts:
            sql += " WHERE " + " AND ".join(parts)
        sql += " ORDER BY id DESC"

        rows = await conn.fetch(sql, *params)
        return [dict(r) for r in rows]
    except Exception as err:
        logger.error("Errore in find_suggerimenti: %s", err)
        raise


async def create_suggerimento(
    conn: asyncpg.Connection, suggerimento: dict
) -> Optional[dict]:
    """Crea un nuovo suggerimento."""
    try:
        sql = """
            INSERT INTO suggerimento (id_mittente, data, stato)
            VALUES ($1, NOW(), 'richiesto')
            RETURNING id, id_mittente, data, stato
        """
        row = await conn.fetchrow(sql, suggerimento["id_mittente"])
        return dict(row) if row else None
    except Exception as err:
        logger.error("Errore in create_suggerimento: %s", err)
        raise


async def update_suggerimento_stato(
    conn: asyncpg.Connection, id_suggerimento: int, stato: str
) -> bool:
    """Aggiorna lo stato di un suggerimento."""
    try:
        sql = "UPDATE suggerimento SET stato=$1 WHERE id=$2"
        status = await conn.execute(sql, stato, id_suggerimento)
        return _rows_affected(status) > 0
    except Exception as err:
        logger.error("Errore in update_suggerimento_stato: %s", err)
        raise
