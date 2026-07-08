"""
DAO per l'entità Utente.
Porting 1:1 di GoodExchangeBE/dao/utenteDao.js in Python/asyncpg.

Note sulla traduzione:
- connection.query(sql, params) → conn.fetch/fetchrow/fetchval/execute(sql, *params)
- result.rows → [dict(r) for r in records]
- result.rowCount > 0 → int(status.split()[-1]) > 0
"""

import logging
from typing import Optional

import asyncpg

logger = logging.getLogger(__name__)


def _rows_affected(status: str) -> int:
    """Estrae il numero di righe modificate dalla stringa di stato asyncpg (es. 'UPDATE 2')."""
    try:
        return int(status.split()[-1])
    except (ValueError, IndexError):
        return 0


async def update_utente_cauzione(
    conn: asyncpg.Connection, id_utente: int, nuovo_valore: float
) -> bool:
    """Aggiorna la cauzione di un utente."""
    try:
        sql = "UPDATE utente SET cauzione=$1 WHERE id=$2"
        status = await conn.execute(sql, nuovo_valore, id_utente)
        return _rows_affected(status) > 0
    except Exception as err:
        logger.error("Errore in update_utente_cauzione: %s", err)
        raise


async def find_utenti(conn: asyncpg.Connection, filtri: dict) -> list[dict]:
    """
    Restituisce una lista filtrata di utenti.
    La clausola WHERE viene costruita dinamicamente dai filtri forniti.
    Porting di findUtenti() in utenteDao.js.
    """
    try:
        sql = "SELECT * FROM utente"
        params: list = []
        parts: list[str] = []

        for campo, valore in filtri.items():
            if valore is None or valore == "":
                continue
            if campo in ("citta", "regione", "provincia", "via"):
                parts.append(f"{campo} ILIKE ${len(params) + 1}")
                params.append(valore if "%" in str(valore) else f"%{valore}%")
            else:
                parts.append(f"{campo} = ${len(params) + 1}")
                params.append(valore)

        if parts:
            sql += " WHERE " + " AND ".join(parts)

        rows = await conn.fetch(sql, *params)
        utenti_list = [dict(r) for r in rows]
        # Arricchimento read-only con reputazione calcolata al volo dai feedback (senza UPDATE che abortiscono transazioni)
        for u in utenti_list:
            try:
                sql_rep = "SELECT ROUND(AVG(voto)::numeric, 2) as media FROM feedback WHERE id_destinatario = $1"
                row_rep = await conn.fetchrow(sql_rep, u["id"])
                media = row_rep["media"] if row_rep and row_rep["media"] is not None else None
                u["reputazione"] = float(media) if media is not None else None
            except Exception:
                if "reputazione" not in u:
                    u["reputazione"] = None
        return utenti_list
    except Exception as err:
        logger.error("Errore in find_utenti: %s", err)
        raise


async def find_utente_by_id(conn: asyncpg.Connection, id_utente: int) -> Optional[dict]:
    """Restituisce un utente per ID o None se non trovato. Calcola la reputazione al volo in read-only per totale sicurezza."""
    try:
        sql = "SELECT * FROM utente WHERE id=$1"
        row = await conn.fetchrow(sql, id_utente)
        if not row:
            return None
        
        utente_dict = dict(row)
        try:
            sql_rep = "SELECT ROUND(AVG(voto)::numeric, 2) as media FROM feedback WHERE id_destinatario = $1"
            row_rep = await conn.fetchrow(sql_rep, id_utente)
            media = row_rep["media"] if row_rep and row_rep["media"] is not None else None
            utente_dict["reputazione"] = float(media) if media is not None else None
        except Exception:
            if "reputazione" not in utente_dict:
                utente_dict["reputazione"] = None
        return utente_dict
    except Exception as err:
        logger.error("Errore in find_utente_by_id: %s", err)
        raise


async def find_utente_by_username(
    conn: asyncpg.Connection, username: str
) -> Optional[dict]:
    """Restituisce un utente per username o None se non trovato. Calcola la reputazione al volo in read-only."""
    try:
        sql = "SELECT * FROM utente WHERE username=$1"
        row = await conn.fetchrow(sql, username)
        if not row:
            return None
        
        utente_dict = dict(row)
        try:
            sql_rep = "SELECT ROUND(AVG(voto)::numeric, 2) as media FROM feedback WHERE id_destinatario = $1"
            row_rep = await conn.fetchrow(sql_rep, utente_dict["id"])
            media = row_rep["media"] if row_rep and row_rep["media"] is not None else None
            utente_dict["reputazione"] = float(media) if media is not None else None
        except Exception:
            if "reputazione" not in utente_dict:
                utente_dict["reputazione"] = None
        return utente_dict
    except Exception as err:
        logger.error("Errore in find_utente_by_username: %s", err)
        raise


async def create_utente(conn: asyncpg.Connection, utente: dict) -> Optional[dict]:
    """
    Inserisce un nuovo utente nel database.
    Porting di createUtente() in utenteDao.js.
    Restituisce il dict utente con l'id generato o None se fallisce.
    """
    try:
        sql = """
            INSERT INTO utente
                (username, password, nome, cognome, codice_fiscale,
                 regione, provincia, citta, via, civico,
                 ruolo, stato, crediti_valore_beni, crediti_accumulati, cauzione)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
            RETURNING id
        """
        params = [
            utente["username"],
            utente["password"],
            utente["nome"],
            utente["cognome"],
            utente["codice_fiscale"],
            utente["regione"],
            utente["provincia"],
            utente["citta"],
            utente["via"],
            utente["civico"],
            utente.get("ruolo", "utente"),
            "attivo",
            0,
            0,
            0.00,
        ]
        row = await conn.fetchrow(sql, *params)
        if row is None:
            return None
        return {**utente, "id_utente": row["id"], "id": row["id"]}
    except Exception as err:
        logger.error("Errore in create_utente: %s", err)
        raise


async def update_utente(
    conn: asyncpg.Connection, id_utente: int, aggiornamento: dict
) -> list:
    """
    Aggiornamento dinamico dei campi di un utente.
    Porting di updateUtente() in utenteDao.js.
    """
    try:
        parts: list[str] = []
        params: list = []

        for campo, valore in aggiornamento.items():
            if valore is None or valore == "":
                continue
            parts.append(f"{campo} = ${len(params) + 1}")
            params.append(valore)

        if not parts:
            return []

        sql = "UPDATE utente SET " + ", ".join(parts)
        sql += f" WHERE id = ${len(params) + 1}"
        params.append(id_utente)

        await conn.execute(sql, *params)
        return []
    except Exception as err:
        logger.error("Errore in update_utente: %s", err)
        raise


async def update_utente_stato(
    conn: asyncpg.Connection, id_utente: int, stato: str
) -> bool:
    """Aggiorna lo stato (attivo/disattivo) di un utente."""
    try:
        sql = "UPDATE utente SET stato=$1 WHERE id=$2"
        status = await conn.execute(sql, stato, id_utente)
        return _rows_affected(status) > 0
    except Exception as err:
        logger.error("Errore in update_utente_stato: %s", err)
        raise


async def calcola_crediti_valore_beni(conn: asyncpg.Connection, id_utente: int) -> int:
    """
    Calcola la somma dei crediti delle categorie dei beni messi a disposizione dall'utente
    e aggiorna il campo crediti_valore_beni.
    Porting di calcolaCreditiValoreBeni() in utenteDao.js.
    """
    try:
        sql_aggregata = """
            SELECT COALESCE(SUM(c.crediti), 0) as totale
            FROM bene b JOIN categoria c ON b.id_categoria = c.id
            WHERE b.id_proprietario = $1
        """
        totale = await conn.fetchval(sql_aggregata, id_utente)
        await conn.execute(
            "UPDATE utente SET crediti_valore_beni = $1 WHERE id = $2",
            totale,
            id_utente,
        )
        return int(totale)
    except Exception as err:
        logger.error("Errore in calcola_crediti_valore_beni: %s", err)
        raise


async def calcola_crediti_accumulati(conn: asyncpg.Connection, id_utente: int) -> int:
    """
    Calcola la somma dei crediti guadagnati tramite prestiti completati.
    Aggiorna il campo crediti_accumulati dell'utente.
    Porting di calcolaCreditiAccumulati() in utenteDao.js.
    """
    try:
        sql_aggregata = """
            SELECT COALESCE(SUM(c.crediti), 0) as totale
            FROM prestito p
            JOIN bene b ON p.id_bene = b.id
            JOIN categoria c ON b.id_categoria = c.id
            WHERE p.id_proprietario = $1 AND p.stato = 'completato'
        """
        totale = await conn.fetchval(sql_aggregata, id_utente)
        await conn.execute(
            "UPDATE utente SET crediti_accumulati = $1 WHERE id = $2",
            totale,
            id_utente,
        )
        return int(totale)
    except Exception as err:
        logger.error("Errore in calcola_crediti_accumulati: %s", err)
        raise
