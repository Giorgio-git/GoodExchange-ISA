"""
DAO per l'entità Messaggio.
Porting 1:1 di GoodExchangeBE/dao/messaggioDao.js in Python/asyncpg.
"""

import logging
from typing import Optional

import asyncpg

logger = logging.getLogger(__name__)


async def create_messaggio(conn: asyncpg.Connection, messaggio: dict) -> int:
    """Crea un nuovo messaggio e restituisce il suo ID."""
    try:
        sql = """
            INSERT INTO messaggio (id_mittente, id_destinatario, titolo, contenuto, tipo, id_riferito)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
        """
        row = await conn.fetchrow(
            sql,
            messaggio["id_mittente"],
            messaggio["id_destinatario"],
            messaggio.get("titolo", "senza titolo"),
            messaggio["contenuto"],
            messaggio["tipo"],
            messaggio["id_riferito"],
        )
        return row["id"]
    except Exception as err:
        logger.error("Errore in create_messaggio: %s", err)
        raise


async def find_messaggio_by_id(
    conn: asyncpg.Connection, id_messaggio: int
) -> Optional[dict]:
    """Recupera un messaggio per ID."""
    try:
        sql = "SELECT * FROM messaggio WHERE id=$1"
        row = await conn.fetchrow(sql, id_messaggio)
        return dict(row) if row else None
    except Exception as err:
        logger.error("Errore in find_messaggio_by_id: %s", err)
        raise


async def find_messaggi_by_destinatario(
    conn: asyncpg.Connection, id_destinatario: int
) -> list[dict]:
    """Restituisce tutti i messaggi ricevuti da un utente."""
    try:
        sql = "SELECT * FROM messaggio WHERE id_destinatario=$1 ORDER BY id DESC"
        rows = await conn.fetch(sql, id_destinatario)
        return [dict(r) for r in rows]
    except Exception as err:
        logger.error("Errore in find_messaggi_by_destinatario: %s", err)
        raise


async def find_messaggi_by_mittente(
    conn: asyncpg.Connection, id_mittente: int
) -> list[dict]:
    """Restituisce tutti i messaggi inviati da un utente."""
    try:
        sql = "SELECT * FROM messaggio WHERE id_mittente=$1 ORDER BY id DESC"
        rows = await conn.fetch(sql, id_mittente)
        return [dict(r) for r in rows]
    except Exception as err:
        logger.error("Errore in find_messaggi_by_mittente: %s", err)
        raise


async def find_messaggi_by_tipo(conn: asyncpg.Connection, tipo: str) -> list[dict]:
    """Restituisce tutti i messaggi di un certo tipo."""
    try:
        sql = "SELECT * FROM messaggio WHERE tipo=$1 ORDER BY id DESC"
        rows = await conn.fetch(sql, tipo)
        return [dict(r) for r in rows]
    except Exception as err:
        logger.error("Errore in find_messaggi_by_tipo: %s", err)
        raise


async def find_messaggi_by_tipo_and_riferito(
    conn: asyncpg.Connection, tipo: str, id_riferito: int
) -> list[dict]:
    """Restituisce messaggi filtrati per tipo e id_riferito."""
    try:
        sql = (
            "SELECT * FROM messaggio WHERE tipo=$1 AND id_riferito=$2 ORDER BY id DESC"
        )
        rows = await conn.fetch(sql, tipo, id_riferito)
        return [dict(r) for r in rows]
    except Exception as err:
        logger.error("Errore in find_messaggi_by_tipo_and_riferito: %s", err)
        raise


async def update_messaggio(
    conn: asyncpg.Connection, id_messaggio: int, aggiornamenti: dict
) -> None:
    """Aggiornamento dinamico di un messaggio."""
    try:
        parts: list[str] = []
        params: list = []

        for campo, valore in aggiornamenti.items():
            parts.append(f"{campo} = ${len(params) + 1}")
            params.append(valore)

        if not parts:
            return

        sql = "UPDATE messaggio SET " + ", ".join(parts)
        sql += f" WHERE id = ${len(params) + 1}"
        params.append(id_messaggio)
        await conn.execute(sql, *params)
    except Exception as err:
        logger.error("Errore in update_messaggio: %s", err)
        raise


async def delete_messaggio(conn: asyncpg.Connection, id_messaggio: int) -> None:
    """Elimina un messaggio per ID."""
    try:
        sql = "DELETE FROM messaggio WHERE id=$1"
        await conn.execute(sql, id_messaggio)
    except Exception as err:
        logger.error("Errore in delete_messaggio: %s", err)
        raise
