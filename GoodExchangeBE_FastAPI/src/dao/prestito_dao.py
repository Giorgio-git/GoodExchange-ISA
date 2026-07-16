"""
DAO per l'entità Prestito.
Porting 1:1 di GoodExchangeBE/dao/PrestitoDao.js in Python/asyncpg.

NOTA ARCHITETTURALE: Le funzioni create_prestito e update_stato_prestito
sono state spostate in src/services/prestito_service.py perché contengono
logica transazionale complessa (Strict 2PL, FSM, side-effects multi-entità).
Questo DAO contiene solo operazioni atomiche pure di lettura e supporto.
"""

import logging
from datetime import date
from typing import Optional

import asyncpg

from src.dao.utente_dao import _rows_affected

logger = logging.getLogger(__name__)


async def find_prestiti(conn: asyncpg.Connection, filters: dict) -> list[dict]:
    """
    Restituisce una lista filtrata di prestiti con dati JOIN su bene e utenti.
    Porting di findPrestiti() in PrestitoDao.js.
    """
    try:
        sql = """
            SELECT p.*,
                   b.nome as bene_nome,
                   ub.username as beneficiario_username,
                   up.username as proprietario_username
            FROM prestito p
            LEFT JOIN bene b ON p.id_bene = b.id
            LEFT JOIN utente ub ON p.id_beneficiario = ub.id
            LEFT JOIN utente up ON p.id_proprietario = up.id
        """
        params: list = []
        parts: list[str] = []

        for campo, valore in filters.items():
            if valore is None or valore == "":
                continue

            if campo == "data_da":
                parts.append(f"p.data_fine >= ${len(params) + 1}")
                params.append(valore)
            elif campo == "data_a":
                parts.append(f"p.data_inizio <= ${len(params) + 1}")
                params.append(valore)
            elif campo == "id_beneficiario":
                parts.append(f"p.id_beneficiario = ${len(params) + 1}")
                params.append(valore)
            else:
                parts.append(f"p.{campo} = ${len(params) + 1}")
                params.append(valore)

        if parts:
            sql += " WHERE " + " AND ".join(parts)

        sql += " ORDER BY p.data DESC"

        rows = await conn.fetch(sql, *params)
        return [dict(r) for r in rows]
    except Exception as err:
        logger.error("Errore in find_prestiti: %s", err)
        raise


async def find_prestito_by_id(
    conn: asyncpg.Connection, id_prestito: int
) -> Optional[dict]:
    """
    Recupera un prestito per ID con dati JOIN su bene e utenti.
    Porting di findPrestitoById() in PrestitoDao.js.
    """
    try:
        sql = """
            SELECT p.*,
                   b.nome as bene_nome,
                   ub.username as beneficiario_username,
                   up.username as proprietario_username
            FROM prestito p
            LEFT JOIN bene b ON p.id_bene = b.id
            LEFT JOIN utente ub ON p.id_beneficiario = ub.id
            LEFT JOIN utente up ON p.id_proprietario = up.id
            WHERE p.id = $1
        """
        row = await conn.fetchrow(sql, id_prestito)
        return dict(row) if row else None
    except Exception as err:
        logger.error("Errore in find_prestito_by_id: %s", err)
        raise


async def verifica_disponibilita(
    conn: asyncpg.Connection,
    bene_id: int,
    data_inizio: date,
    data_fine: date,
) -> bool:
    """
    Verifica che non esistano prestiti in stato 'accettato' o 'in_corso'
    che si sovrappongono al periodo richiesto (intersezione intervalli).
    Porting di verificaDisponibilita() in PrestitoDao.js.

    Restituisce True se il bene è disponibile, False altrimenti.
    """
    try:
        sql = """
            SELECT COUNT(*) as conflitti
            FROM prestito
            WHERE id_bene = $1
              AND stato IN ('accettato', 'in_corso')
              AND (
                  (data_inizio <= $2 AND data_fine >= $3) OR
                  (data_inizio <= $4 AND data_fine >= $5) OR
                  (data_inizio >= $6 AND data_fine <= $7)
              )
        """
        params = [
            bene_id,
            data_inizio,
            data_inizio,
            data_fine,
            data_fine,
            data_inizio,
            data_fine,
        ]
        conflitti = await conn.fetchval(sql, *params)
        return int(conflitti) == 0
    except Exception as err:
        logger.error("Errore in verifica_disponibilita: %s", err)
        raise


async def get_calendario_bene(
    conn: asyncpg.Connection, bene_id: int, anno: int, mese: int
) -> list[dict]:
    """
    Restituisce i prestiti attivi per un bene in un mese specifico.
    Porting di getCalendarioBene() in PrestitoDao.js.
    """
    try:
        import calendar
        from datetime import date as date_type

        primo_giorno = date_type(anno, mese, 1)
        ultimo_giorno = date_type(anno, mese, calendar.monthrange(anno, mese)[1])

        sql = """
            SELECT p.data_inizio, p.data_fine, p.stato,
                   ub.username as beneficiario_username
            FROM prestito p
            LEFT JOIN utente ub ON p.id_beneficiario = ub.id
            WHERE p.id_bene = $1
              AND p.stato IN ('accettato', 'in_corso')
              AND (
                  (EXTRACT(YEAR FROM p.data_inizio) = $2 AND EXTRACT(MONTH FROM p.data_inizio) = $3) OR
                  (EXTRACT(YEAR FROM p.data_fine) = $4 AND EXTRACT(MONTH FROM p.data_fine) = $5) OR
                  (p.data_inizio <= $6 AND p.data_fine >= $7)
              )
            ORDER BY p.data_inizio
        """
        params = [bene_id, anno, mese, anno, mese, primo_giorno, ultimo_giorno]
        rows = await conn.fetch(sql, *params)
        return [dict(r) for r in rows]
    except Exception as err:
        logger.error("Errore in get_calendario_bene: %s", err)
        raise


async def delete_prestito(conn: asyncpg.Connection, id_prestito: int) -> bool:
    """Elimina un prestito per ID. Porting di deletePrestito() in PrestitoDao.js."""
    try:
        sql = "DELETE FROM prestito WHERE id = $1"
        status = await conn.execute(sql, id_prestito)
        return _rows_affected(status) > 0
    except Exception as err:
        logger.error("Errore in delete_prestito: %s", err)
        raise
