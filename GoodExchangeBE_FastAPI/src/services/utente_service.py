"""
Service Layer per l'entità Utente.

Incapsula la logica di business relativa agli utenti che va oltre
la semplice persistenza (DAO). In particolare:

- La verifica di solvibilità è una funzione
  pura testabile indipendentemente dal database.
- La registrazione utente centralizza le regole di business sul ruolo
  e sui valori iniziali dei crediti.

Design by Contract:
    verifica_solvibilita_utente:
        Pre:  cauzione >= 0 AND crediti_accumulati >= 0 AND valore_bene > 0
        Post: return == (cauzione + crediti_accumulati) >= valore_bene

Architettura Three-Tier:
  utente_router.py → utente_service.py → utente_dao.py
"""

import logging
from typing import Optional

import asyncpg

from src.dao import utente_dao

logger = logging.getLogger(__name__)


def verifica_solvibilita_utente(
    cauzione: float,
    crediti_accumulati: float,
    valore_bene: float,
) -> bool:
    """
    Verifica se un utente ha capacità di credito sufficiente per richiedere
    un bene.

    Funzione pura: nessun accesso al database, nessun side-effect.
    Testabile con Property-Based Testing (Hypothesis).

    Design by Contract:
        Pre:  cauzione >= 0
        Pre:  crediti_accumulati >= 0
        Pre:  valore_bene > 0
        Post: return == (cauzione + crediti_accumulati) >= valore_bene

    Proprietà PBT verificata da test:
        FOR ALL cauzione >= 0, crediti_accumulati >= 0, valore_bene > 0:
            verifica_solvibilita_utente(c, ca, vb) == ((c + ca) >= vb)

    Args:
        cauzione: Cauzione figurativa dell'utente (>= 0).
        crediti_accumulati: Crediti guadagnati con prestiti completati (>= 0).
        valore_bene: Valore in crediti della categoria del bene (> 0).

    Returns:
        True se l'utente è solvibile, False altrimenti.

    Raises:
        ValueError: Se i parametri violano le pre-condizioni.
    """
    if cauzione < 0:
        raise ValueError(f"cauzione deve essere >= 0, ricevuto: {cauzione}")
    if crediti_accumulati < 0:
        raise ValueError(
            f"crediti_accumulati deve essere >= 0, ricevuto: {crediti_accumulati}"
        )
    if valore_bene <= 0:
        raise ValueError(f"valore_bene deve essere > 0, ricevuto: {valore_bene}")

    return (cauzione + crediti_accumulati) >= valore_bene


async def registra_utente(
    conn: asyncpg.Connection,
    utente_data: dict,
) -> Optional[dict]:
    """
    Registra un nuovo utente con i valori iniziali corretti.

    Centralizza la Business Rule sul ruolo predefinito ('utente') e
    garantisce che i crediti iniziali siano sempre zero.

    Design by Contract:
        Pre:  utente_data contiene username, password, nome, cognome,
              codice_fiscale, regione, provincia, citta, via, civico
        Pre:  username non esiste già in T_Utenti
        Pre:  codice_fiscale non esiste già in T_Utenti
        Post: utente creato in T_Utenti con stato='attivo',
              ruolo='utente', crediti_valore_beni=0,
              crediti_accumulati=0, cauzione=0.

    Args:
        conn: Connessione asyncpg (dentro una transazione attiva del router).
        utente_data: Dict con i dati anagrafici dell'utente.

    Returns:
        Dict dell'utente creato (senza password), o None se la creazione fallisce.
    """
    logger.info("registra_utente: username=%s", utente_data.get("username"))

    # Imposta i valori predefiniti di dominio
    utente_data.setdefault("ruolo", "utente")

    # Crea l'utente tramite DAO
    utente_creato = await utente_dao.create_utente(conn, utente_data)
    if not utente_creato:
        logger.error(
            "Creazione utente fallita nel DAO per username=%s",
            utente_data.get("username"),
        )
        return None

    logger.info(
        "Utente %s registrato con successo (id=%s).",
        utente_data.get("username"),
        utente_creato.get("id"),
    )

    # Rimuovi la password prima di restituire
    return {k: v for k, v in utente_creato.items() if k != "password"}
