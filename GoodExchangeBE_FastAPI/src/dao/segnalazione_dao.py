"""
DAO per Segnalazione.
Porting 1:1 di GoodExchangeBE/dao/segnalazioneDao.js in Python/asyncpg.
"""

import logging
from typing import Optional

import asyncpg

from src.dao.utente_dao import _rows_affected

logger = logging.getLogger(__name__)


async def create_segnalazione(
    conn: asyncpg.Connection, segnalazione: dict
) -> Optional[dict]:
    """Crea una nuova segnalazione."""
    try:
        sql = """
            INSERT INTO segnalazione (id_segnalante, id_segnalato, data, stato)
            VALUES ($1, $2, NOW(), $3)
            RETURNING id
        """
        row = await conn.fetchrow(
            sql,
            segnalazione["id_segnalante"],
            segnalazione.get("id_segnalato"),
            segnalazione.get("stato", "aperta"),
        )
        if row is None:
            return None
        return {**segnalazione, "id": row["id"]}
    except Exception as err:
        logger.error("Errore in create_segnalazione: %s", err)
        raise


async def find_segnalazioni(conn: asyncpg.Connection, filtri: dict) -> list[dict]:
    """Restituisce una lista filtrata di segnalazioni."""
    try:
        sql = "SELECT * FROM segnalazione"
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
        logger.error("Errore in find_segnalazioni: %s", err)
        raise


async def find_segnalazione_by_id(
    conn: asyncpg.Connection, id_segnalazione: int
) -> Optional[dict]:
    """Recupera una segnalazione per ID."""
    try:
        sql = "SELECT * FROM segnalazione WHERE id=$1"
        row = await conn.fetchrow(sql, id_segnalazione)
        return dict(row) if row else None
    except Exception as err:
        logger.error("Errore in find_segnalazione_by_id: %s", err)
        raise


async def update_segnalazione_stato(
    conn: asyncpg.Connection, id_segnalazione: int, stato: str
) -> bool:
    """Aggiorna lo stato di una segnalazione."""
    try:
        sql = "UPDATE segnalazione SET stato=$1 WHERE id=$2"
        status = await conn.execute(sql, stato, id_segnalazione)
        return _rows_affected(status) > 0
    except Exception as err:
        logger.error("Errore in update_segnalazione_stato: %s", err)
        raise
