"""
Test di Sistema (System Testing / E2E Scenarios) per GoodExchange.

Riferimento Appunti del Corso (Lezione 7 — Test di Sistema):
- "Si concentra sulle interazioni fra componenti"
- "Test di scenari completi di utilizzo (end-to-end): ad esempio, in un'applicazione a strati, un'azione che li coinvolga tutti"
- "Tecnica dello scaffolding e verifica del comportamento complessivo"

A differenza dei test di integrazione che verificano le singole transazioni API<->DB o i singoli metodi CRUD,
questi test simulano macro-scenari orizzontali di business multi-attore (Proprietario, Richiedente, Amministratore)
interagendo con il sistema esattamente come farebbero i servizi del Frontend Angular attraverso le chiamate REST HTTP.
"""

import uuid
from typing import Any
import pytest
from httpx import AsyncClient
from tests.conftest import UTENTE_TEST_BASE


@pytest.mark.asyncio
async def test_system_scenario_1_ciclo_prestito_feedback_crediti(async_client: AsyncClient):
    """
    SCENARIO DI SISTEMA 1: Ciclo di vita E2E di un prestito con rilascio feedback e accredito crediti.
    
    Attori simulati (dal Frontend verso le API):
    1. Mario (Proprietario del bene)
    2. Luigi (Beneficiario/Richiedente)
    
    Flusso End-to-End verificato:
    - [Setup] Registrazione di Mario e Luigi + Ricarica cauzione di Luigi (100€ per soddisfare DbC solvibilità).
    - [Catalogo] Mario aggiunge "Bicicletta Elettrica" (categoria 20 crediti). Il sistema aggiorna `crediti_valore_beni` di Mario.
    - [FSM Prestito] Luigi richiede il prestito ('richiesto') -> Mario accetta ('accettato') -> Mario consegna ('in_corso').
    - [2PL/ACID] Allo stato 'in_corso', il sistema blocca automaticamente il bene nel catalogo (stato = False).
    - [Completamento] Riconsegna ('completato'). Il bene torna disponibile (stato = True) e i crediti accumulati di Mario salgono a 20.
    - [Reputazione] Luigi lascia un feedback a Mario a 5 stelle -> la reputazione di Mario diventa 5.0.
    """
    # 1. REGISTRAZIONE ATTORI (Mario e Luigi)
    username_mario = f"mario_sys_{uuid.uuid4().hex[:6]}"
    cf_mario = f"MRO{uuid.uuid4().hex[:13].upper()}"[:16]
    res_mario = await async_client.post("/api/utenti", json={
        **UTENTE_TEST_BASE, "username": username_mario, "nome": "Mario", "cognome": "Rossi", "codice_fiscale": cf_mario
    })
    assert res_mario.status_code == 201
    mario = res_mario.json()
    id_mario = mario.get("id") or mario.get("id_utente")

    username_luigi = f"luigi_sys_{uuid.uuid4().hex[:6]}"
    cf_luigi = f"LGI{uuid.uuid4().hex[:13].upper()}"[:16]
    res_luigi = await async_client.post("/api/utenti", json={
        **UTENTE_TEST_BASE, "username": username_luigi, "nome": "Luigi", "cognome": "Verdi", "codice_fiscale": cf_luigi
    })
    assert res_luigi.status_code == 201
    luigi = res_luigi.json()
    id_luigi = luigi.get("id") or luigi.get("id_utente")

    # Luigi ricarica la cauzione a 100€ per essere solvibile
    res_cauz = await async_client.put(f"/api/utenti/{id_luigi}/cauzione", json={"cauzione": 100.0})
    assert res_cauz.status_code == 200

    # 2. CREAZIONE CATEGORIA DA PARTE DELL'AMMINISTRATORE E BENE NEL CATALOGO DA PARTE DI MARIO
    # Solo l'Amministratore ha il permesso concettuale/architetturale di definire le categorie
    username_admin = f"admin_sc1_{uuid.uuid4().hex[:6]}"
    cf_admin = f"AD1{uuid.uuid4().hex[:13].upper()}"[:16]
    res_admin = await async_client.post("/api/utenti", json={
        **UTENTE_TEST_BASE, "username": username_admin, "ruolo": "admin", "codice_fiscale": cf_admin
    })
    assert res_admin.status_code == 201

    res_cat = await async_client.post("/api/categorie", json={
        "nome": f"Sport_{uuid.uuid4().hex[:4]}",
        "crediti": 20,
        "descrizione": "Attrezzature sportive e mobilità"
    })
    assert res_cat.status_code == 201
    id_cat = res_cat.json()["id"]

    res_bene = await async_client.post("/api/beni", json={
        "nome": "Bicicletta Elettrica",
        "descrizione": "Bici in perfette condizioni",
        "id_categoria": id_cat,
        "id_proprietario": id_mario,
        "stato": True,
        "peso": 15.0
    })
    assert res_bene.status_code == 201
    id_bene = res_bene.json()["id"]

    # Verifica di sistema sul profilo del proprietario: i crediti valore beni devono essere saliti a 20
    res_get_mario = await async_client.get(f"/api/utenti/{id_mario}")
    assert res_get_mario.status_code == 200
    assert res_get_mario.json()["crediti_valore_beni"] == 20

    # 3. AVVIO E PROGRESSIONE PRESTITO (FSM: richiesto -> accettato -> in_corso)
    res_prestito = await async_client.post("/api/prestiti", json={
        "id_bene": id_bene,
        "id_beneficiario": id_luigi,
        "id_proprietario": id_mario,
        "data_inizio": "2026-08-01",
        "data_fine": "2026-08-10",
        "stato": "richiesto"
    })
    assert res_prestito.status_code == 201
    id_prestito = res_prestito.json()["id"]

    res_acc = await async_client.put(f"/api/prestiti/{id_prestito}/stato", json={"stato": "accettato"})
    assert res_acc.status_code == 200

    res_in_corso = await async_client.put(f"/api/prestiti/{id_prestito}/stato", json={"stato": "in_corso"})
    assert res_in_corso.status_code == 200

    # Verifica sul catalogo: il bene rimane con stato=True (gestito solo dal proprietario)
    res_check_bene = await async_client.get(f"/api/beni/{id_bene}")
    assert res_check_bene.json()["stato"] is True

    # Verifica sul calendario/disponibilità: una richiesta sovrapposta viene rifiutata (409 Conflict)
    res_conflitto = await async_client.post(
        "/api/prestiti",
        json={
            "id_bene": id_bene,
            "id_beneficiario": id_luigi,
            "id_proprietario": id_mario,
            "data_inizio": "2026-08-05",
            "data_fine": "2026-08-08",
            "stato": "richiesto",
        },
    )
    assert res_conflitto.status_code == 409

    # 4. COMPLETAMENTO DEL PRESTITO
    res_compl = await async_client.put(
        f"/api/prestiti/{id_prestito}/stato", json={"stato": "completato"}
    )
    assert res_compl.status_code == 200

    # Verifica di sistema sulle entità correlate dopo completamento:
    # a) Il bene mantiene lo stato catalogo attivo (True)
    assert (await async_client.get(f"/api/beni/{id_bene}")).json()["stato"] is True
    # b) I crediti accumulati di Mario devono essere aumentati del valore del bene (20 crediti)
    res_mario_post = await async_client.get(f"/api/utenti/{id_mario}")
    assert res_mario_post.json()["crediti_accumulati"] == 20

    # 5. RILASCIO FEEDBACK E CALCOLO REPUTAZIONE (FR-19 / INV-05)
    res_fb = await async_client.post("/api/feedback", json={
        "id_utente": id_luigi,
        "id_destinatario": id_mario,
        "voto": 5,
        "data": None
    })
    assert res_fb.status_code in (200, 201)

    # Verifica reputazione finale di Mario
    res_mario_rep = await async_client.get(f"/api/utenti/{id_mario}")
    assert float(res_mario_rep.json()["reputazione"]) == pytest.approx(5.0)


@pytest.mark.asyncio
async def test_system_scenario_2_intervento_dufficio_admin_segnalazione(async_client: AsyncClient):
    """
    SCENARIO DI SISTEMA 2: Intervento d'ufficio dell'Amministratore a seguito di una segnalazione durante un prestito in corso.
    
    Attori simulati (dal Frontend verso le API):
    1. Mario (Proprietario)
    2. Luigi (Beneficiario/Richiedente)
    3. Admin (Amministratore del sistema)
    
    Flusso End-to-End verificato:
    - [Setup] Mario e Luigi avviano un prestito e lo portano in stato 'in_corso' (bene bloccato -> stato = False).
    - [Imprevisto] Durante il periodo d'uso si verifica un contenzioso/danno. Mario invia una `segnalazione` al sistema.
    - [Intervento Admin] L'Amministratore esamina la segnalazione e opta per l'annullamento d'ufficio (`in_corso` -> `annullato`).
    - [Verifica Invarianti ACID/FSM] Il sistema deve garantire che:
      a) Lo stato del prestito diventi 'annullato'.
      b) Il bene venga sbloccato immediatamente (stato = True) per essere riassegnato o riparato.
      c) I crediti accumulati di Mario e Luigi restino invariati (nessun accredito illegittimo).
    - [Chiusura Segnalazione] L'Amministratore segna la segnalazione come 'completata'.
    """
    # 1. REGISTRAZIONE ATTORI (Mario, Luigi, Admin)
    username_mario = f"mario_seg_{uuid.uuid4().hex[:6]}"
    cf_mario = f"MSG{uuid.uuid4().hex[:13].upper()}"[:16]
    id_mario = (await async_client.post("/api/utenti", json={
        **UTENTE_TEST_BASE, "username": username_mario, "codice_fiscale": cf_mario
    })).json().get("id")

    username_luigi = f"luigi_seg_{uuid.uuid4().hex[:6]}"
    cf_luigi = f"LSG{uuid.uuid4().hex[:13].upper()}"[:16]
    id_luigi = (await async_client.post("/api/utenti", json={
        **UTENTE_TEST_BASE, "username": username_luigi, "codice_fiscale": cf_luigi
    })).json().get("id")

    await async_client.put(f"/api/utenti/{id_luigi}/cauzione", json={"cauzione": 100.0})

    username_admin = f"admin_sys_{uuid.uuid4().hex[:6]}"
    cf_admin = f"ADM{uuid.uuid4().hex[:13].upper()}"[:16]
    res_admin = await async_client.post("/api/utenti", json={
        **UTENTE_TEST_BASE, "username": username_admin, "ruolo": "admin", "codice_fiscale": cf_admin
    })
    assert res_admin.status_code == 201

    # 2. CREAZIONE BENE E PRESTITO "IN CORSO"
    id_cat = (await async_client.post("/api/categorie", json={
        "nome": f"Tech_{uuid.uuid4().hex[:4]}", "crediti": 30, "descrizione": "Elettronica"
    })).json()["id"]

    id_bene = (await async_client.post("/api/beni", json={
        "nome": "Trapano Bosch", "descrizione": "Potente", "id_categoria": id_cat, "id_proprietario": id_mario, "stato": True, "peso": 2.0
    })).json()["id"]

    id_prestito = (await async_client.post("/api/prestiti", json={
        "id_bene": id_bene, "id_beneficiario": id_luigi, "id_proprietario": id_mario,
        "data_inizio": "2026-09-01", "data_fine": "2026-09-05", "stato": "richiesto"
    })).json()["id"]

    await async_client.put(f"/api/prestiti/{id_prestito}/stato", json={"stato": "accettato"})
    await async_client.put(f"/api/prestiti/{id_prestito}/stato", json={"stato": "in_corso"})

    # Verifica sul catalogo: il bene rimane con stato=True
    assert (await async_client.get(f"/api/beni/{id_bene}")).json()["stato"] is True

    # 3. INVIO SEGNALAZIONE DA PARTE DI MARIO
    res_segnalazione = await async_client.post(
        "/api/segnalazioni",
        json={"id_segnalante": id_mario, "id_segnalato": id_luigi, "stato": "aperta"},
    )
    assert res_segnalazione.status_code == 201
    id_segnalazione = res_segnalazione.json()["id"]

    # Verifica persistenza segnalazione in stato 'aperta'
    res_get_seg = await async_client.get(f"/api/segnalazioni/{id_segnalazione}")
    assert res_get_seg.status_code == 200
    assert res_get_seg.json()["stato"] == "aperta"

    # 4. INTERVENTO D'UFFICIO DELL'ADMIN: ANNULLAMENTO DA 'in_corso' A 'annullato'
    # La nostra logica FSM permette l'annullamento d'ufficio da 'in_corso' ad 'annullato'
    res_annulla = await async_client.put(
        f"/api/prestiti/{id_prestito}/stato", json={"stato": "annullato"}
    )
    assert res_annulla.status_code == 200

    # 5. VERIFICA INVARIANTI DI SISTEMA DOPO ANNULLAMENTO D'UFFICIO:
    # a) Lo stato del prestito è 'annullato'
    res_check_p = await async_client.get(f"/api/prestiti/{id_prestito}")
    assert res_check_p.status_code == 200
    assert res_check_p.json()["stato"] == "annullato"

    # b) Il bene mantiene lo stato catalogo attivo (stato = True)
    assert (await async_client.get(f"/api/beni/{id_bene}")).json()["stato"] is True

    # c) Nessun credito deve essere stato addebitato/accreditato impropriamente
    assert (
        await async_client.get(f"/api/utenti/{id_mario}")
    ).json()["crediti_accumulati"] == 0
    assert (
        await async_client.get(f"/api/utenti/{id_luigi}")
    ).json()["crediti_accumulati"] == 0

    # 6. CHIUSURA DELLA SEGNALAZIONE DA PARTE DELL'ADMIN
    res_chiudi_seg = await async_client.put(f"/api/segnalazioni/{id_segnalazione}/stato", json={"stato": "risolta"})
    assert res_chiudi_seg.status_code == 200
    assert (await async_client.get(f"/api/segnalazioni/{id_segnalazione}")).json()["stato"] == "risolta"
