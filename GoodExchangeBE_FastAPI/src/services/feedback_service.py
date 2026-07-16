"""
Service Layer per l'entità Feedback.

Incapsula la logica di business del feedback che va oltre la semplice
persistenza: al momento della creazione di un feedback, la reputazione
media del destinatario deve essere aggiornata atomicamente.

Design by Contract:
    Pre:  voto IN {1,2,3,4,5}
    Pre:  id_utente != id_destinatario
    Post: feedback creato in T_Feedback
    Post: utente[id_destinatario].reputazione = AVG(tutti i voti ricevuti)
    Invariante: reputazione IN [1.0, 5.0]

Architettura Three-Tier:
  feedback_router.py → feedback_service.py → feedback_dao.py + utente_dao.py
"""

import logging
from typing import Optional

import asyncpg

from src.dao import feedback_dao

logger = logging.getLogger(__name__)


async def crea_feedback_e_aggiorna_reputazione(
    conn: asyncpg.Connection,
    feedback_data: dict,
) -> Optional[dict]:
    """
    Crea un feedback e aggiorna atomicamente la reputazione media
    del destinatario come media aritmetica di tutti i voti ricevuti.

    Design by Contract:
        Pre:  feedback_data['voto'] IN {1, 2, 3, 4, 5}
        Pre:  feedback_data['id_utente'] != feedback_data['id_destinatario']
        Post: feedback inserito in T_Feedback
        Post: utente[id_destinatario].reputazione = AVG(voti ricevuti)

    Args:
        conn: Connessione asyncpg (dentro una transazione attiva del router).
        feedback_data: Dict con id_utente, id_destinatario, voto, data (opzionale).

    Returns:
        Dict del feedback creato con l'id generato, o None se la creazione fallisce.
    """
    id_destinatario = feedback_data["id_destinatario"]
    voto = feedback_data["voto"]

    logger.info(
        "crea_feedback_e_aggiorna_reputazione: da=%s, a=%s, voto=%s",
        feedback_data.get("id_utente"),
        id_destinatario,
        voto,
    )

    # 1. Crea il feedback
    feedback_creato = await feedback_dao.create_feedback(conn, feedback_data)
    if not feedback_creato:
        logger.error("Creazione feedback fallita nel DAO.")
        return None

    # 2. Calcola la nuova reputazione media del destinatario
    nuova_reputazione = await feedback_dao.calcola_reputazione_media(
        conn, id_destinatario
    )

    # 3. Aggiorna il campo reputazione del destinatario
    await feedback_dao.aggiorna_reputazione_utente(
        conn, id_destinatario, nuova_reputazione
    )

    logger.info(
        "Feedback %s creato. Reputazione utente %s aggiornata a %.2f.",
        feedback_creato["id"],
        id_destinatario,
        nuova_reputazione,
    )
    return feedback_creato


def calcola_reputazione_media_locale(voti: list[int]) -> float:
    """
    Calcola la media aritmetica di una lista di voti.

    Funzione pura (nessun side-effect) testabile con Property-Based Testing
    (Hypothesis).

    Design by Contract:
        Pre:  len(voti) > 0
        Pre:  ogni voto IN {1, 2, 3, 4, 5}
        Post: return IN [1.0, 5.0]
        Post: return == sum(voti) / len(voti)

    Args:
        voti: Lista non vuota di voti (interi da 1 a 5).

    Returns:
        Media aritmetica dei voti come float.

    Raises:
        ValueError: Se la lista di voti è vuota.
    """
    if not voti:
        raise ValueError("La lista di voti non può essere vuota.")
    return sum(voti) / len(voti)
