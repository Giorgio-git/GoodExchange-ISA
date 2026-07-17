"""
DAO per l'entità Recensione.
"""

import logging
from typing import Optional

import asyncpg

from src.dao.utente_dao import _rows_affected

logger = logging.getLogger(__name__)


async def find_recensioni(conn: asyncpg.Connection, filtri: dict) -> list[dict]:
    """Restituisce una lista filtrata di recensioni."""
    try:
        sql = "SELECT * FROM recensione"
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
        logger.error("Errore in find_recensioni: %s", err)
        raise


async def find_recensione_by_id(
    conn: asyncpg.Connection, id_recensione: int
) -> Optional[dict]:
    """Recupera una recensione per ID."""
    try:
        sql = "SELECT * FROM recensione WHERE id=$1"
        row = await conn.fetchrow(sql, id_recensione)
        return dict(row) if row else None
    except Exception as err:
        logger.error("Errore in find_recensione_by_id: %s", err)
        raise


async def create_recensione(
    conn: asyncpg.Connection, recensione: dict
) -> Optional[dict]:
    """Crea una nuova recensione."""
    try:
        sql = """
            INSERT INTO recensione (id_bene, id_beneficiario, voto, data)
            VALUES ($1, $2, $3, NOW())
            RETURNING id
        """
        row = await conn.fetchrow(
            sql,
            recensione["id_bene"],
            recensione["id_beneficiario"],
            recensione["voto"],
        )
        if row is None:
            return None
        return {**recensione, "id": row["id"]}
    except Exception as err:
        logger.error("Errore in create_recensione: %s", err)
        raise


async def update_recensione(
    conn: asyncpg.Connection, id_recensione: int, aggiornamento: dict
) -> bool:
    """Aggiornamento dinamico di una recensione."""
    try:
        parts: list[str] = []
        params: list = []

        for campo, valore in aggiornamento.items():
            if valore is None:
                continue
            parts.append(f"{campo} = ${len(params) + 1}")
            params.append(valore)

        if not parts:
            return False

        sql = "UPDATE recensione SET " + ", ".join(parts)
        sql += f" WHERE id = ${len(params) + 1}"
        params.append(id_recensione)

        status = await conn.execute(sql, *params)
        return _rows_affected(status) > 0
    except Exception as err:
        logger.error("Errore in update_recensione: %s", err)
        raise


async def delete_recensione(conn: asyncpg.Connection, id_recensione: int) -> bool:
    """Elimina una recensione per ID."""
    try:
        sql = "DELETE FROM recensione WHERE id=$1"
        status = await conn.execute(sql, id_recensione)
        return _rows_affected(status) > 0
    except Exception as err:
        logger.error("Errore in delete_recensione: %s", err)
        raise
