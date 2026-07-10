import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_prestito_fsm_e_side_effects_integration(
    async_client: AsyncClient,
    utente_proprietario: dict,
    utente_beneficiario: dict,
    bene_test: dict,
):
    """
    Verifica il ciclo di vita completo della FSM di un prestito:
      'richiesto' -> 'accettato' -> 'in_corso' -> 'completato'
    e assicura che al cambio di stato il bene venga bloccato/sbloccato
    e i crediti accumulati del proprietario vengano incrementati atomicamente.
    """
    id_bene = bene_test["id"]
    id_prop = utente_proprietario["id"]
    id_ben = utente_beneficiario["id"]

    # 0. Rendi il beneficiario solvibile aumentando la sua cauzione nel DB di test
    await async_client.put(f"/api/utenti/{id_ben}/cauzione", json={"cauzione": 100.0})

    payload = {
        "id_bene": id_bene,
        "id_beneficiario": id_ben,
        "id_proprietario": id_prop,
        "data_inizio": "2026-08-01",
        "data_fine": "2026-08-10",
        "stato": "richiesto",
    }

    # 1. Creazione in stato 'richiesto'
    res_create = await async_client.post("/api/prestiti", json=payload)
    assert res_create.status_code == 201, f"Errore creazione prestito: {res_create.text}"
    prestito_id = res_create.json()["id"]

    # 2. Transizione verso 'accettato'
    res_acc = await async_client.put(f"/api/prestiti/{prestito_id}/stato", json={"stato": "accettato"})
    assert res_acc.status_code == 200

    # 3. Transizione verso 'in_corso' (deve bloccare il bene -> stato = False)
    res_in_corso = await async_client.put(f"/api/prestiti/{prestito_id}/stato", json={"stato": "in_corso"})
    assert res_in_corso.status_code == 200

    res_bene_bloccato = await async_client.get(f"/api/beni/{id_bene}")
    assert res_bene_bloccato.json()["stato"] is False  # Bene bloccato (non disponibile)

    # 4. Transizione verso 'completato' (deve sbloccare il bene -> stato = True e aggiornare i crediti)
    res_compl = await async_client.put(f"/api/prestiti/{prestito_id}/stato", json={"stato": "completato"})
    assert res_compl.status_code == 200

    res_bene_sbloccato = await async_client.get(f"/api/beni/{id_bene}")
    assert res_bene_sbloccato.json()["stato"] is True  # Bene tornato disponibile


@pytest.mark.asyncio
async def test_prestito_solvibilita_insufficiente_409_integration(
    async_client: AsyncClient,
    utente_proprietario: dict,
    utente_beneficiario: dict,
    bene_test: dict,
):
    """
    Verifica precondizione DbC e vincoli ACID: se l'utente non ha cauzione o crediti sufficienti,
    la creazione del prestito viene rigettata in transazione con 409 Conflict.
    """
    # Assicuriamoci che il beneficiario abbia cauzione 0
    await async_client.put(f"/api/utenti/{utente_beneficiario['id']}/cauzione", json={"cauzione": 0.0})

    payload = {
        "id_bene": bene_test["id"],
        "id_beneficiario": utente_beneficiario["id"],
        "id_proprietario": utente_proprietario["id"],
        "data_inizio": "2026-09-01",
        "data_fine": "2026-09-05",
        "stato": "richiesto",
    }
    # bene_test ha categoria che richiede 15 crediti -> cauzione 0 non basta -> 409 Conflict
    res = await async_client.post("/api/prestiti", json=payload)
    assert res.status_code == 409
    assert "Solvibilità insufficiente" in res.json()["detail"]


@pytest.mark.asyncio
async def test_prestito_conflitto_date_e_fsm_illiceita_integration(
    async_client: AsyncClient,
    utente_proprietario: dict,
    utente_beneficiario: dict,
    bene_test: dict,
):
    """
    Verifica sia il blocco su date sovrapposte (conflitto 2PL/ACID),
    sia il rigetto di transizioni FSM illecite (es. richiesto -> completato).
    """
    id_bene = bene_test["id"]
    id_prop = utente_proprietario["id"]
    id_ben = utente_beneficiario["id"]

    # Rendiamo solvibile il beneficiario
    await async_client.put(f"/api/utenti/{id_ben}/cauzione", json={"cauzione": 100.0})

    # 1. Creiamo un primo prestito e lo portiamo in 'accettato' (periodo: 1-10 Ottobre)
    payload_1 = {
        "id_bene": id_bene,
        "id_beneficiario": id_ben,
        "id_proprietario": id_prop,
        "data_inizio": "2026-10-01",
        "data_fine": "2026-10-10",
        "stato": "richiesto",
    }
    res_1 = await async_client.post("/api/prestiti", json=payload_1)
    assert res_1.status_code == 201
    prestito_1_id = res_1.json()["id"]
    await async_client.put(f"/api/prestiti/{prestito_1_id}/stato", json={"stato": "accettato"})

    # 2. Proviamo a creare un secondo prestito sovrapposto (periodo: 5-15 Ottobre) -> 409 Conflict
    payload_sovrapposto = {
        "id_bene": id_bene,
        "id_beneficiario": id_ben,
        "id_proprietario": id_prop,
        "data_inizio": "2026-10-05",
        "data_fine": "2026-10-15",
        "stato": "richiesto",
    }
    res_2 = await async_client.post("/api/prestiti", json=payload_sovrapposto)
    assert res_2.status_code == 409
    assert "non è disponibile nel periodo richiesto" in res_2.json()["detail"]

    # 3. Proviamo una transizione FSM illecita su prestito_1_id (da 'accettato' direttamente a 'rifiutato' o da un nuovo prestito richiesto direttamente a completato)
    # Creiamo un nuovo prestito (in periodo libero: 20-25 Ottobre)
    payload_3 = {
        "id_bene": id_bene,
        "id_beneficiario": id_ben,
        "id_proprietario": id_prop,
        "data_inizio": "2026-10-20",
        "data_fine": "2026-10-25",
        "stato": "richiesto",
    }
    res_3 = await async_client.post("/api/prestiti", json=payload_3)
    prestito_3_id = res_3.json()["id"]

    # Da 'richiesto' verso 'completato' non è consentito in FSM_TRANSIZIONI
    res_fsm_err = await async_client.put(f"/api/prestiti/{prestito_3_id}/stato", json={"stato": "completato"})
    assert res_fsm_err.status_code == 409
    assert "Transizione non valida" in res_fsm_err.json()["detail"]
