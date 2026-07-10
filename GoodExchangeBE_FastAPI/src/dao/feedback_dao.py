"""
DAO per l'entità Feedback.
Porting 1:1 di GoodExchangeBE/dao/feedbackDao.js in Python/asyncpg.
"""

import logging
from typing import Optional

import asyncpg

from src.dao.utente_dao import _rows_affected

logger = logging.getLogger(__name__)


async def find_feedback_by_user_id(
    conn: asyncpg.Connection, id_utente: int
) -> list[dict]:
    """Restituisce tutti i feedback dove l'utente è destinatario."""
    try:
        sql = "SELECT * FROM feedback WHERE id_destinatario=$1 ORDER BY id DESC"
        rows = await conn.fetch(sql, id_utente)
        return [dict(r) for r in rows]
    except Exception as err:
        logger.error("Errore in find_feedback_by_user_id: %s", err)
        raise


async def find_feedback_by_username(
    conn: asyncpg.Connection, username: str
) -> list[dict]:
    """
    Restituisce i feedback per un utente identificato per username.
    Porting di findFeedbackByUsername() in feedbackDao.js.
    Nota: il codice JS originale aveva un bug (controllava rowsUtente.length
    invece di rowsUtente.rows.length); qui viene implementato correttamente.
    """
    try:
        sql_utente = "SELECT id FROM utente WHERE username=$1"
        row_utente = await conn.fetchrow(sql_utente, username)
        if not row_utente:
            return []
        id_destinatario = row_utente["id"]

        sql_feedback = """
            SELECT * FROM feedback
            WHERE id_destinatario=$1
            ORDER BY id DESC
        """
        rows = await conn.fetch(sql_feedback, id_destinatario)
        return [dict(r) for r in rows]
    except Exception as err:
        logger.error("Errore in find_feedback_by_username: %s", err)
        raise


async def create_feedback(conn: asyncpg.Connection, feedback: dict) -> Optional[dict]:
    """Crea un nuovo feedback."""
    try:
        sql = """
            INSERT INTO feedback (id_utente, id_destinatario, voto, data)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        row = await conn.fetchrow(
            sql,
            feedback["id_utente"],
            feedback["id_destinatario"],
            feedback["voto"],
            feedback.get("data"),
        )
        if row is None:
            return None
        return {**feedback, "id": row["id"]}
    except Exception as err:
        logger.error("Errore in create_feedback: %s", err)
        raise


async def delete_feedback(conn: asyncpg.Connection, id_feedback: int) -> bool:
    """Elimina un feedback per ID (solo admin)."""
    try:
        sql = "DELETE FROM feedback WHERE id=$1"
        status = await conn.execute(sql, id_feedback)
        return _rows_affected(status) > 0
    except Exception as err:
        logger.error("Errore in delete_feedback: %s", err)
        raise


async def calcola_reputazione_media(
    conn: asyncpg.Connection, id_destinatario: int
) -> float:
    """
    Calcola la reputazione media di un utente come media aritmetica
    di tutti i feedback ricevuti.

    Questa funzione è chiamata da feedback_service dopo ogni nuovo feedback
    per aggiornare atomicamente la reputazione (SRS §FR-19, §9.4).

    Args:
        conn: Connessione asyncpg.
        id_destinatario: ID dell'utente di cui calcolare la reputazione.

    Returns:
        Media aritmetica dei voti (float in [1.0, 5.0]),
        o 0.0 se l'utente non ha ancora feedback.
    """
    try:
        sql = """
            SELECT COALESCE(AVG(voto), 0.0) AS media
            FROM feedback
            WHERE id_destinatario = $1
        """
        media = await conn.fetchval(sql, id_destinatario)
        return float(media)
    except Exception as err:
        logger.error("Errore in calcola_reputazione_media: %s", err)
        raise


async def aggiorna_reputazione_utente(
    conn: asyncpg.Connection, id_utente: int, nuova_reputazione: float
) -> None:
    """
    Aggiorna il campo 'reputazione' dell'utente nel database.
    Se la colonna non esiste su vecchi schemi, cattura il warning senza abortire la transazione.
    """
    try:
        async with conn.transaction():
            sql = "UPDATE utente SET reputazione = $1 WHERE id = $2"
            await conn.execute(sql, nuova_reputazione, id_utente)
    except Exception as err:
        logger.warning(
            "Nota durante aggiornamento colonna reputazione per utente %s: %s",
            id_utente,
            err,
        )
