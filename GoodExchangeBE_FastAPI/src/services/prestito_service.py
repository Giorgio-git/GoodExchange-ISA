"""
Service Layer per la gestione dei Prestiti.
Contiene la logica di business complessa che coordina più DAO:
- Strict 2PL (SELECT ... FOR UPDATE) per prevenire Lost Update concorrenti
- FSM (Finite State Machine) per le transizioni di stato valide
- Calcolo e aggiornamento dei crediti utente al cambio di stato
- notifica_delivery: funzione mockabile per test con hypothesis

Riferimenti architetturali (dal documento di contesto del corso):
- Sezione 2.5: FSM degli stati del prestito
- Sezione 3.3: Design by Contract (precondizioni esplicite)
- Sezione 4.4: Strict 2PL per la gestione delle race condition
"""

import logging
from datetime import date

import asyncpg
import httpx

from src.dao import bene_dao, prestito_dao, utente_dao

logger = logging.getLogger(__name__)

# ——————————————————————————————————————————————
# FSM: Mappa delle transizioni di stato valide
# (Sezione 2.5 del documento di contesto del corso)
# ——————————————————————————————————————————————
FSM_TRANSIZIONI: dict[str, set[str]] = {
    "richiesto": {"accettato", "rifiutato", "annullato"},
    "accettato": {"in_corso", "annullato"},
    "in_corso": {"completato", "annullato"},
    "completato": set(),  # stato finale
    "rifiutato": set(),  # stato finale
    "annullato": set(),  # stato finale
}


# ——————————————————————————————————————————————
# Design by Contract — funzione pura testabile con Hypothesis
# ——————————————————————————————————————————————
def verifica_solvibilita_utente(
    cauzione: float,
    crediti_valore_beni: int,
    soglia_cauzione: float = 0.0,
    soglia_crediti: int = 0,
) -> bool:
    """
    Verifica che un utente soddisfi i requisiti minimi per richiedere un prestito.

    Precondizioni (Design by Contract — Sezione 3.3):
    - cauzione >= 0
    - crediti_valore_beni >= 0

    Questa funzione è pura (nessun side-effect) e quindi testabile con Hypothesis.
    """
    assert cauzione >= 0, "cauzione deve essere non-negativa"
    assert crediti_valore_beni >= 0, "crediti_valore_beni deve essere non-negativo"
    return cauzione >= soglia_cauzione and crediti_valore_beni >= soglia_crediti


# ——————————————————————————————————————————————
# notifica_delivery: simulazione notifica esterna (mockabile nei test)
# ——————————————————————————————————————————————
async def notifica_delivery(prestito_id: int, stato: str) -> bool:
    """
    Invia una notifica HTTP a un servizio esterno (simulato) quando
    un prestito raggiunge lo stato 'completato'.
    Questa funzione è mockabile via unittest.mock.AsyncMock nei test.

    In produzione sarebbe un webhook reale; qui punta a localhost come mock.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                "http://localhost:9999/webhook/delivery",
                json={"prestito_id": prestito_id, "stato": stato},
            )
            return response.status_code == 200
    except httpx.RequestError as e:
        logger.warning("Notifica delivery fallita (ignorabile in dev): %s", e)
        return False


# ——————————————————————————————————————————————
# FASE 1: Creazione prestito con verifica disponibilità
# ——————————————————————————————————————————————
async def crea_prestito(
    conn: asyncpg.Connection,
    id_bene: int,
    id_beneficiario: int,
    id_proprietario: int,
    data_inizio: date,
    data_fine: date,
) -> dict:
    """
    Crea un prestito nello stato 'richiesto'.

    Logica (Strict 2PL + Design by Contract):
    1. Verifica che data_fine > data_inizio (precondizione)
    2. Verifica disponibilità del bene nel periodo richiesto
    3. Inserisce il prestito in stato 'richiesto'

    La transazione esterna (in prestito_router.py) garantisce l'atomicità.
    Porting della logica in prestitoRouter.js (POST /prestiti).
    """
    # Precondizione: date valide
    if data_fine <= data_inizio:
        raise ValueError("data_fine deve essere successiva a data_inizio")

    # Verifica disponibilità
    disponibile = await prestito_dao.verifica_disponibilita(
        conn, id_bene, data_inizio, data_fine
    )
    if not disponibile:
        raise ValueError(f"Il bene {id_bene} non è disponibile nel periodo richiesto")

    # Inserimento
    sql = """
        INSERT INTO prestito (id_bene, id_beneficiario, id_proprietario, data_inizio, data_fine, stato, data)
        VALUES ($1, $2, $3, $4, $5, 'richiesto', NOW())
        RETURNING *
    """
    row = await conn.fetchrow(
        sql, id_bene, id_beneficiario, id_proprietario, data_inizio, data_fine
    )
    if row is None:
        raise RuntimeError("Creazione prestito fallita")
    return dict(row)


# ——————————————————————————————————————————————
# FASE 2: Aggiornamento stato con Strict 2PL e aggiornamento crediti
# ——————————————————————————————————————————————
async def aggiorna_stato_prestito(
    conn: asyncpg.Connection,
    id_prestito: int,
    nuovo_stato: str,
) -> dict:
    """
    Aggiorna lo stato di un prestito rispettando la FSM.

    Implementa Strict 2PL (Sezione 4.4 del contesto):
    - SELECT ... FOR UPDATE acquisisce il lock esclusivo sulla riga prestito
      impedendo aggiornamenti concorrenti (prevenzione Lost Update)
    - Il lock è rilasciato automaticamente al COMMIT/ROLLBACK della transazione

    Side-effects al cambio di stato:
    - 'in_corso': blocca il bene (stato=False)
    - 'completato': sblocca il bene, aggiorna crediti proprietario, chiama notifica_delivery
    - 'annullato'/'rifiutato': sblocca il bene se era bloccato

    Porting di updateStatoPrestito() in PrestitoDao.js.
    """
    # ——— Strict 2PL: acquisizione lock esclusivo ———
    sql_lock = "SELECT * FROM prestito WHERE id=$1 FOR UPDATE"
    prestito_row = await conn.fetchrow(sql_lock, id_prestito)

    if prestito_row is None:
        raise ValueError(f"Prestito {id_prestito} non trovato")

    prestito = dict(prestito_row)
    stato_corrente = prestito["stato"]

    # ——— Validazione FSM ———
    transizioni_valide = FSM_TRANSIZIONI.get(stato_corrente, set())
    if nuovo_stato not in transizioni_valide:
        raise ValueError(
            f"Transizione non valida: {stato_corrente} → {nuovo_stato}. "
            f"Transizioni consentite: {sorted(transizioni_valide)}"
        )

    # ——— Aggiornamento stato ———
    await conn.execute(
        "UPDATE prestito SET stato=$1 WHERE id=$2",
        nuovo_stato,
        id_prestito,
    )

    # ——— Side-effects in base al nuovo stato ———
    id_bene = prestito["id_bene"]
    id_proprietario = prestito["id_proprietario"]

    if nuovo_stato == "in_corso":
        # Il bene viene prelevato: lo segniamo come non disponibile
        await bene_dao.block_bene(conn, id_bene)
        logger.info("Bene %s bloccato per prestito %s", id_bene, id_prestito)

    elif nuovo_stato == "completato":
        # Il bene è tornato: lo rendiamo di nuovo disponibile
        await bene_dao.unblock_bene(conn, id_bene)
        # Aggiorna i crediti accumulati dal proprietario
        await utente_dao.calcola_crediti_accumulati(conn, id_proprietario)
        logger.info(
            "Prestito %s completato — crediti aggiornati per utente %s",
            id_prestito,
            id_proprietario,
        )
        # notifica_delivery è fuori transazione (effetto collaterale idempotente)
        # Viene chiamata nel router dopo il COMMIT
        await notifica_delivery(id_prestito, nuovo_stato)

    elif nuovo_stato in ("annullato", "rifiutato"):
        # Se il bene era stato bloccato (stato in_corso → annullato), lo sblocchiamo
        # In altri casi (richiesto → rifiutato) il bene era già disponibile
        await bene_dao.unblock_bene(conn, id_bene)
        logger.info(
            "Prestito %s %s — bene %s reso disponibile",
            id_prestito,
            nuovo_stato,
            id_bene,
        )

    # Restituisce il prestito aggiornato
    aggiornato = await conn.fetchrow("SELECT * FROM prestito WHERE id=$1", id_prestito)
    return dict(aggiornato)
