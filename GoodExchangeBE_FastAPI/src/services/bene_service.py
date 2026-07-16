"""
Service Layer per l'entità Bene.

Incapsula la logica di business relativa ai Beni che va
oltre la semplice persistenza (DAO). In particolare:

- La creazione di un bene deve aggiornare atomicamente i crediti_valore_beni
  del proprietario (Design by Contract).
- L'eliminazione di un bene deve ricalcolare atomicamente i crediti_valore_beni.

Architettura Three-Tier:
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

    Design by Contract:
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

    Design by Contract:
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


async def blocca_bene_con_crediti(
    conn: asyncpg.Connection,
    id_bene: int,
) -> bool:
    """
    Blocca un bene (imposta stato=False) e ricalcola atomicamente
    i crediti_valore_beni del proprietario (poiché i beni bloccati
    non generano crediti di cauzione a disposizione).
    """
    bene = await bene_dao.find_bene_by_id(conn, id_bene)
    if not bene:
        return False
    success = await bene_dao.block_bene(conn, id_bene)
    if success:
        await utente_dao.calcola_crediti_valore_beni(conn, bene["id_proprietario"])
        logger.info("Bene %s bloccato. Crediti proprietario %s ricalcolati.", id_bene, bene["id_proprietario"])
    return success


async def sblocca_bene_con_crediti(
    conn: asyncpg.Connection,
    id_bene: int,
) -> bool:
    """
    Sblocca un bene (imposta stato=True) e ricalcola atomicamente
    i crediti_valore_beni del proprietario (il bene torna a generare
    crediti di cauzione a disposizione).
    """
    bene = await bene_dao.find_bene_by_id(conn, id_bene)
    if not bene:
        return False
    success = await bene_dao.unblock_bene(conn, id_bene)
    if success:
        await utente_dao.calcola_crediti_valore_beni(conn, bene["id_proprietario"])
        logger.info("Bene %s sbloccato. Crediti proprietario %s ricalcolati.", id_bene, bene["id_proprietario"])
    return success


async def aggiorna_bene_con_crediti(
    conn: asyncpg.Connection,
    id_bene: int,
    aggiornamenti: dict,
) -> bool:
    """
    Aggiorna un bene e, se la modifica coinvolge la categoria o lo stato,
    ricalcola atomicamente i crediti_valore_beni del proprietario.
    """
    bene = await bene_dao.find_bene_by_id(conn, id_bene)
    if not bene:
        return False
    success = await bene_dao.update_bene(conn, id_bene, aggiornamenti)
    if success and ("id_categoria" in aggiornamenti or "stato" in aggiornamenti):
        await utente_dao.calcola_crediti_valore_beni(conn, bene["id_proprietario"])
        logger.info("Bene %s aggiornato. Crediti proprietario %s ricalcolati.", id_bene, bene["id_proprietario"])
    return success
