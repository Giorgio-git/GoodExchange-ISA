"""
DAO per PreferitiItem.
Porting 1:1 di GoodExchangeBE/dao/preferitiItemDao.js in Python/asyncpg.

La tabella usa virgolette per il nome case-sensitive: "preferitiItem"
"""

import logging

import asyncpg

from src.dao.utente_dao import _rows_affected

logger = logging.getLogger(__name__)


async def get_utenti_preferiti(
    conn: asyncpg.Connection, id_preferiti: int
) -> list[dict]:
    """Recupera tutti gli utenti preferiti di una lista preferiti."""
    try:
        sql = 'SELECT * FROM "preferitiItem" WHERE id=$1'
        rows = await conn.fetch(sql, id_preferiti)
        return [dict(r) for r in rows]
    except Exception as err:
        logger.error("Errore in get_utenti_preferiti: %s", err)
        raise


async def add_utente_preferito(
    conn: asyncpg.Connection, id_preferiti: int, id_utente_preferito: int
) -> bool:
    """Aggiunge un utente alla lista preferiti. Porting di addUtentePreferito() in preferitiItemDao.js."""
    try:
        sql = 'INSERT INTO "preferitiItem" (id, id_utente_preferito) VALUES ($1, $2) RETURNING id'
        row = await conn.fetchrow(sql, id_preferiti, id_utente_preferito)
        return row is not None
    except Exception as err:
        logger.error("Errore in add_utente_preferito: %s", err)
        raise


async def remove_utente_preferito(
    conn: asyncpg.Connection, id_preferiti: int, id_utente_preferito: int
) -> bool:
    """Rimuove un utente dalla lista preferiti. Porting di removeUtentePreferito() in preferitiItemDao.js."""
    try:
        sql = 'DELETE FROM "preferitiItem" WHERE id=$1 AND id_utente_preferito=$2'
        status = await conn.execute(sql, id_preferiti, id_utente_preferito)
        return _rows_affected(status) > 0
    except Exception as err:
        logger.error("Errore in remove_utente_preferito: %s", err)
        raise
