"""
Service Layer per l'entità Bene.

Incapsula la logica di business relativa ai Beni che va
oltre la semplice persistenza (DAO). In particolare:

- La creazione di un bene deve aggiornare atomicamente i crediti_valore_beni
  del proprietario (Design by Contract — SRS §FR-08).
- L'eliminazione di un bene deve ricalcolare atomicamente i crediti_valore_beni
  (SRS §FR-04).

Architettura Three-Tier (SRS §NFR-03):
  bene_router.py → bene_service.py → bene_dao.py + utente_dao.py

Il service non gestisce le transazioni: responsabilità del router
(async with conn.transaction()). Il service riceve la connessione
già dentro una transazione attiva.
"""

import logging
from typing import Optional

import asyncpg

from src.dao import bene_dao, utente_dao

logger = logging.getLogger(__name__)


async def crea_bene_con_crediti(
    conn: asyncpg.Connection,
    bene_data: dict,
) -> Optional[dict]:
    """
    Crea un nuovo bene e aggiorna atomicamente i crediti_valore_beni
    del proprietario.

    Design by Contract (SRS §9):
        Pre:  bene_data contiene id_proprietario, id_categoria, nome
        Pre:  id_proprietario esiste in T_Utenti
        Pre:  id_categoria esiste in T_Categorie
        Post: bene inserito in T_Beni con stato=True
        Post: crediti_valore_beni(proprietario) = Σ categoria.crediti

    Args:
        conn: Connessione asyncpg (dentro una transazione attiva del router).
        bene_data: Dict con i dati del bene.

    Returns:
        Dict del bene creato con l'id generato, o None se la creazione fallisce.
    """
    logger.info(
        "crea_bene_con_crediti: proprietario=%s, categoria=%s",
        bene_data.get("id_proprietario"),
        bene_data.get("id_categoria"),
    )

    # 1. Inserisce il bene nel DB (senza aggiornare i crediti nel DAO)
    bene_creato = await bene_dao.create_bene_raw(conn, bene_data)
    if not bene_creato:
        logger.error("Creazione bene fallita nel DAO.")
        return None

    # 2. Ricalcola atomicamente i crediti_valore_beni del proprietario
    id_proprietario = bene_data["id_proprietario"]
    await utente_dao.calcola_crediti_valore_beni(conn, id_proprietario)

    logger.info(
        "Bene %s creato. Crediti proprietario %s aggiornati.",
        bene_creato["id"],
        id_proprietario,
    )
    return bene_creato


async def elimina_bene_con_crediti(
    conn: asyncpg.Connection,
    id_bene: int,
    id_proprietario: int,
) -> bool:
    """
    Elimina un bene e ricalcola atomicamente i crediti_valore_beni
    del proprietario.

    Design by Contract (SRS §9):
        Pre:  id_bene esiste in T_Beni con id_proprietario dato
        Post: bene rimosso da T_Beni
        Post: crediti_valore_beni(proprietario) ricalcolato

    Args:
        conn: Connessione asyncpg.
        id_bene: ID del bene da eliminare.
        id_proprietario: ID del proprietario (per ricalcolo crediti).

    Returns:
        True se il bene è stato eliminato, False se non trovato.
    """
    logger.info(
        "elimina_bene_con_crediti: bene=%s, proprietario=%s",
        id_bene,
        id_proprietario,
    )

    # 1. Elimina il bene
    eliminato = await bene_dao.delete_bene(conn, id_bene)
    if not eliminato:
        logger.warning("Bene %s non trovato per eliminazione.", id_bene)
        return False

    # 2. Ricalcola i crediti_valore_beni (il bene è già rimosso)
    await utente_dao.calcola_crediti_valore_beni(conn, id_proprietario)

    logger.info(
        "Bene %s eliminato. Crediti proprietario %s aggiornati.",
        id_bene,
        id_proprietario,
    )
    return True
