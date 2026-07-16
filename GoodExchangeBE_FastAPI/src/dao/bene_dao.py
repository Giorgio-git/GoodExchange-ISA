"""
DAO per l'entità Bene.
Porting 1:1 di GoodExchangeBE/dao/beneDao.js in Python/asyncpg.

Gestione BYTEA: asyncpg restituisce i campi BYTEA come oggetti bytes.
Il campo 'immagine' è escluso dalle query standard e gestito da endpoint dedicati.
"""

import logging
from typing import Optional

import asyncpg

from src.dao.utente_dao import _rows_affected

logger = logging.getLogger(__name__)


async def update_bene_immagine(
    conn: asyncpg.Connection, id_bene: int, file_bytes: bytes
) -> None:
    """Aggiorna il campo immagine BYTEA di un bene."""
    try:
        sql = "UPDATE bene SET immagine = $1 WHERE id = $2"
        await conn.execute(sql, file_bytes, id_bene)
    except Exception as err:
        logger.error("Errore in update_bene_immagine: %s", err)
        raise


async def get_bene_immagine(conn: asyncpg.Connection, id_bene: int) -> Optional[bytes]:
    """Recupera solo il campo immagine BYTEA di un bene."""
    try:
        sql = "SELECT immagine FROM bene WHERE id = $1"
        row = await conn.fetchrow(sql, id_bene)
        if row and row["immagine"]:
            return bytes(row["immagine"])
        return None
    except Exception as err:
        logger.error("Errore in get_bene_immagine: %s", err)
        raise


async def delete_bene_immagine(conn: asyncpg.Connection, id_bene: int) -> None:
    """Azzera il campo immagine di un bene (imposta a NULL)."""
    try:
        sql = "UPDATE bene SET immagine = NULL WHERE id = $1"
        await conn.execute(sql, id_bene)
    except Exception as err:
        logger.error("Errore in delete_bene_immagine: %s", err)
        raise


async def find_beni_by_proprietari(
    conn: asyncpg.Connection, id_proprietari: list[int], stato: Optional[bool] = None
) -> list[dict]:
    """
    Restituisce i beni appartenenti a una lista di proprietari (ricerca per zona).
    Usa ANY($1) di asyncpg per la clausola IN efficiente.
    Porting di findBeniByProprietari() in beneDao.js.
    """
    try:
        if not id_proprietari:
            return []
        if stato is not None:
            sql = """
                SELECT id, id_proprietario, id_categoria, nome, descrizione, peso, stato
                FROM bene
                WHERE id_proprietario = ANY($1) AND stato = $2
                ORDER BY id DESC
            """
            rows = await conn.fetch(sql, id_proprietari, stato)
        else:
            sql = """
                SELECT id, id_proprietario, id_categoria, nome, descrizione, peso, stato
                FROM bene
                WHERE id_proprietario = ANY($1)
                ORDER BY id DESC
            """
            rows = await conn.fetch(sql, id_proprietari)
        return [dict(r) for r in rows]
    except Exception as err:
        logger.error("Errore in find_beni_by_proprietari: %s", err)
        raise


async def find_beni(conn: asyncpg.Connection, filters: dict) -> list[dict]:
    """
    Restituisce una lista filtrata di beni (senza immagine).
    Supporta: filtri esatti su campi validi, ricerca testuale 'search', sort, limit.
    Porting di findBeni() in beneDao.js.
    """
    try:
        sql = "SELECT id, id_proprietario, id_categoria, nome, descrizione, peso, stato FROM bene"
        params: list = []
        parts: list[str] = []

        # Campi validi per il filtraggio diretto
        valid_bene_fields = {
            "id",
            "id_proprietario",
            "id_categoria",
            "nome",
            "descrizione",
            "peso",
            "stato",
            "foto",
        }

        for campo, valore in filters.items():
            if valore is None or valore == "":
                continue
            if campo in ("limit", "sort"):
                continue

            if campo == "search":
                n = len(params) + 1
                parts.append(f"nome ILIKE ${n}")
                params.append(f"%{valore}%")
            elif campo in valid_bene_fields:
                parts.append(f"{campo} = ${len(params) + 1}")
                params.append(valore)

        if parts:
            sql += " WHERE " + " AND ".join(parts)

        # Ordinamento
        if filters.get("sort") == "random":
            sql += " ORDER BY RANDOM()"
        else:
            sql += " ORDER BY id DESC"

        # Limite risultati
        if filters.get("limit"):
            sql += f" LIMIT ${len(params) + 1}"
            params.append(int(filters["limit"]))

        logger.info("SQL query: %s", sql)
        logger.info("Params: %s", params)
        rows = await conn.fetch(sql, *params)
        return [dict(r) for r in rows]
    except Exception as err:
        logger.error("Errore in find_beni: %s", err)
        logger.error("Stack trace: %s", err)
        raise


async def find_bene_by_id(conn: asyncpg.Connection, id_bene: int) -> Optional[dict]:
    """
    Recupera un bene per ID (senza il campo immagine per evitare dati binari in JSON).
    Porting di findBeneById() in beneDao.js.
    """
    try:
        sql = "SELECT id, id_proprietario, id_categoria, nome, descrizione, peso, stato FROM bene WHERE id=$1"
        row = await conn.fetchrow(sql, id_bene)
        return dict(row) if row else None
    except Exception as err:
        logger.error("Errore in find_bene_by_id: %s", err)
        raise


async def create_bene_raw(conn: asyncpg.Connection, bene: dict) -> Optional[dict]:
    """
    Inserisce un nuovo bene nel database (senza aggiornare i crediti).

    Questa funzione è chiamata da bene_service.crea_bene_con_crediti(),
    che si occupa di aggiornare i crediti_valore_beni del proprietario
    nel service layer (Architettura Three-Tier).

    Args:
        conn: Connessione asyncpg.
        bene: Dict con id_proprietario, id_categoria, nome, descrizione, peso, stato.

    Returns:
        Dict del bene con l'id generato, o None se l'INSERT fallisce.
    """
    try:
        sql = """
            INSERT INTO bene (id_proprietario, id_categoria, nome, descrizione, peso, stato, immagine)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id
        """
        params = [
            bene["id_proprietario"],
            bene["id_categoria"],
            bene["nome"],
            bene.get("descrizione"),
            bene.get("peso"),
            bene.get("stato", True),
            None,  # immagine gestita separatamente via endpoint dedicato
        ]
        row = await conn.fetchrow(sql, *params)
        if row is None:
            return None
        return {**bene, "id": row["id"]}
    except Exception as err:
        logger.error("Errore in create_bene_raw: %s", err)
        raise


async def update_bene(
    conn: asyncpg.Connection, id_bene: int, aggiornamenti: dict
) -> bool:
    """
    Aggiornamento dinamico dei campi validi di un bene.
    Porting di updateBene() in beneDao.js.
    """
    try:
        valid_bene_fields = {
            "id_proprietario",
            "id_categoria",
            "nome",
            "descrizione",
            "peso",
            "stato",
            "foto",
        }
        parts: list[str] = []
        params: list = []

        for campo, valore in aggiornamenti.items():
            if campo not in valid_bene_fields:
                continue
            parts.append(f"{campo} = ${len(params) + 1}")
            params.append(valore)

        if not parts:
            return False

        sql = "UPDATE bene SET " + ", ".join(parts)
        sql += f" WHERE id = ${len(params) + 1}"
        params.append(id_bene)

        status = await conn.execute(sql, *params)
        return _rows_affected(status) > 0
    except Exception as err:
        logger.error("Errore in update_bene: %s", err)
        raise


async def block_bene(conn: asyncpg.Connection, id_bene: int) -> bool:
    """Imposta lo stato del bene a False (occupato). Porting di blockBene()."""
    try:
        sql = "UPDATE bene SET stato=$1 WHERE id=$2"
        status = await conn.execute(sql, False, id_bene)
        return _rows_affected(status) > 0
    except Exception as err:
        logger.error("Errore in block_bene: %s", err)
        raise


async def unblock_bene(conn: asyncpg.Connection, id_bene: int) -> bool:
    """Imposta lo stato del bene a True (disponibile). Porting di unblockBene()."""
    try:
        sql = "UPDATE bene SET stato=$1 WHERE id=$2"
        status = await conn.execute(sql, True, id_bene)
        return _rows_affected(status) > 0
    except Exception as err:
        logger.error("Errore in unblock_bene: %s", err)
        raise


async def delete_bene(conn: asyncpg.Connection, id_bene: int) -> bool:
    """
    Elimina un bene per ID.

    Nota: il ricalcolo dei crediti_valore_beni del proprietario
    è responsabilità di bene_service.elimina_bene_con_crediti().

    Args:
        conn: Connessione asyncpg.
        id_bene: ID del bene da eliminare.

    Returns:
        True se il bene è stato eliminato, False se non trovato.
    """
    try:
        sql = "DELETE FROM bene WHERE id = $1"
        status = await conn.execute(sql, id_bene)
        return _rows_affected(status) > 0
    except Exception as err:
        logger.error("Errore in delete_bene: %s", err)
        raise
