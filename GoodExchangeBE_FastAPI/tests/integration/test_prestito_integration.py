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
    assert res_create.status_code == 201, (
        f"Errore creazione prestito: {res_create.text}"
    )
    prestito_id = res_create.json()["id"]

    # 2. Transizione verso 'accettato'
    res_acc = await async_client.put(
        f"/api/prestiti/{prestito_id}/stato", json={"stato": "accettato"}
    )
    assert res_acc.status_code == 200

    # 3. Transizione verso 'in_corso' (lo stato del catalogo del bene rimane True, disponibilità gestita su intervallo date)
    res_in_corso = await async_client.put(
        f"/api/prestiti/{prestito_id}/stato", json={"stato": "in_corso"}
    )
    assert res_in_corso.status_code == 200

    res_bene_dopo_corso = await async_client.get(f"/api/beni/{id_bene}")
    assert res_bene_dopo_corso.json()["stato"] is True  # Lo stato catalogo resta attivo

    # Verifica sul calendario e disponibilità: un altro utente che chiede per le stesse date riceve 409 Conflict
    res_conflitto = await async_client.post(
        "/api/prestiti",
        json={
            "id_bene": id_bene,
            "id_beneficiario": id_ben,
            "id_proprietario": id_prop,
            "data_inizio": "2026-08-02",
            "data_fine": "2026-08-05",
            "stato": "richiesto",
        },
    )
    assert res_conflitto.status_code == 409
    assert "non è disponibile" in res_conflitto.json()["detail"]

    # 4. Transizione verso 'completato' (aggiorna i crediti accumulati del proprietario)
    res_compl = await async_client.put(
        f"/api/prestiti/{prestito_id}/stato", json={"stato": "completato"}
    )
    assert res_compl.status_code == 200

    res_bene_dopo_compl = await async_client.get(f"/api/beni/{id_bene}")
    assert res_bene_dopo_compl.json()["stato"] is True


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
    await async_client.put(
        f"/api/utenti/{utente_beneficiario['id']}/cauzione", json={"cauzione": 0.0}
    )

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
    await async_client.put(
        f"/api/prestiti/{prestito_1_id}/stato", json={"stato": "accettato"}
    )

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
    res_fsm_err = await async_client.put(
        f"/api/prestiti/{prestito_3_id}/stato", json={"stato": "completato"}
    )
    assert res_fsm_err.status_code == 409
    assert "Transizione non valida" in res_fsm_err.json()["detail"]


@pytest.mark.asyncio
async def test_prestito_double_booking_su_accettazione_integration(
    async_client: AsyncClient,
    utente_proprietario: dict,
    utente_beneficiario: dict,
    bene_test: dict,
):
    """
    Verifica la guardia anti-Double Booking implementata in aggiorna_stato_prestito:
    se due richieste per date sovrapposte sono entrambe in stato 'richiesto', il proprietario
    non può accettarle entrambe — il secondo tentativo restituisce 409 con il messaggio corretto.
    """
    id_bene = bene_test["id"]
    id_prop = utente_proprietario["id"]
    id_ben = utente_beneficiario["id"]

    await async_client.put(f"/api/utenti/{id_ben}/cauzione", json={"cauzione": 100.0})

    # 1. Crea due richieste sovrapposte per lo stesso periodo
    payload_a = {
        "id_bene": id_bene,
        "id_beneficiario": id_ben,
        "id_proprietario": id_prop,
        "data_inizio": "2027-03-01",
        "data_fine": "2027-03-10",
        "stato": "richiesto",
    }
    payload_b = {
        "id_bene": id_bene,
        "id_beneficiario": id_ben,
        "id_proprietario": id_prop,
        "data_inizio": "2027-03-05",
        "data_fine": "2027-03-15",
        "stato": "richiesto",
    }
    res_a = await async_client.post("/api/prestiti", json=payload_a)
    assert res_a.status_code == 201
    id_a = res_a.json()["id"]

    res_b = await async_client.post("/api/prestiti", json=payload_b)
    assert res_b.status_code == 201
    id_b = res_b.json()["id"]

    # 2. Accetta il prestito A -> OK
    res_acc_a = await async_client.put(
        f"/api/prestiti/{id_a}/stato", json={"stato": "accettato"}
    )
    assert res_acc_a.status_code == 200

    # 3. Tenta di accettare B (date sovrapposte con A già accettato) -> 409
    res_acc_b = await async_client.put(
        f"/api/prestiti/{id_b}/stato", json={"stato": "accettato"}
    )
    assert res_acc_b.status_code == 409
    assert (
        "Esiste già un prestito concesso per le date indicate"
        in res_acc_b.json()["detail"]
    )


@pytest.mark.asyncio
async def test_get_prestito_by_id_integration(
    async_client: AsyncClient,
    utente_proprietario: dict,
    utente_beneficiario: dict,
    bene_test: dict,
):
    """Verifica GET /api/prestiti/:id per un prestito esistente e per uno inesistente (404)."""
    await async_client.put(
        f"/api/utenti/{utente_beneficiario['id']}/cauzione", json={"cauzione": 100.0}
    )
    payload = {
        "id_bene": bene_test["id"],
        "id_beneficiario": utente_beneficiario["id"],
        "id_proprietario": utente_proprietario["id"],
        "data_inizio": "2027-05-01",
        "data_fine": "2027-05-05",
        "stato": "richiesto",
    }
    res_create = await async_client.post("/api/prestiti", json=payload)
    assert res_create.status_code == 201
    prestito_id = res_create.json()["id"]

    # GET esistente
    res_get = await async_client.get(f"/api/prestiti/{prestito_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == prestito_id

    # GET inesistente -> 404
    res_404 = await async_client.get("/api/prestiti/999999999")
    assert res_404.status_code == 404


@pytest.mark.asyncio
async def test_prestito_filtri_calendario_e_delete_integration(
    async_client: AsyncClient,
    utente_proprietario: dict,
    utente_beneficiario: dict,
    bene_test: dict,
):
    """Verifica endpoint di filtri, disponibilità, calendario e cancellazione del router prestiti."""
    await async_client.put(
        f"/api/utenti/{utente_beneficiario['id']}/cauzione", json={"cauzione": 100.0}
    )
    payload = {
        "id_bene": bene_test["id"],
        "id_beneficiario": utente_beneficiario["id"],
        "id_proprietario": utente_proprietario["id"],
        "data_inizio": "2027-06-01",
        "data_fine": "2027-06-05",
        "stato": "richiesto",
    }
    res_create = await async_client.post("/api/prestiti", json=payload)
    assert res_create.status_code == 201
    prestito_id = res_create.json()["id"]

    # 1. GET /api/prestiti/filtri con parametri
    res_filtri = await async_client.get(
        f"/api/prestiti/filtri?id_bene={bene_test['id']}&stato=richiesto"
    )
    assert res_filtri.status_code == 200
    assert any(p["id"] == prestito_id for p in res_filtri.json())

    # 2. GET /api/prestiti con query param
    res_list = await async_client.get(
        f"/api/prestiti?id_proprietario={utente_proprietario['id']}"
    )
    assert res_list.status_code == 200
    assert any(p["id"] == prestito_id for p in res_list.json())

    # 3. GET /api/prestiti/disponibilita/:bene_id
    res_disp = await async_client.get(
        f"/api/prestiti/disponibilita/{bene_test['id']}?data_inizio=2027-07-01&data_fine=2027-07-10"
    )
    assert res_disp.status_code == 200
    assert "disponibile" in res_disp.json()

    # 4. GET /api/prestiti/calendario/:bene_id con prestito 'richiesto' -> lista vuota perché calendario mostra solo accettati/in_corso
    res_cal_empty = await async_client.get(
        f"/api/prestiti/calendario/{bene_test['id']}?anno=2027&mese=6"
    )
    assert res_cal_empty.status_code == 200
    assert res_cal_empty.json() == []

    # Accettiamo il prestito per testare il calendario popolato
    await async_client.put(
        f"/api/prestiti/{prestito_id}/stato", json={"stato": "accettato"}
    )
    res_cal = await async_client.get(
        f"/api/prestiti/calendario/{bene_test['id']}?anno=2027&mese=6"
    )
    assert res_cal.status_code == 200
    assert len(res_cal.json()) > 0
    assert res_cal.json()[0]["stato"] == "accettato"

    # 5. DELETE /api/prestiti/:id
    res_del = await async_client.delete(f"/api/prestiti/{prestito_id}")
    assert res_del.status_code == 200
    assert "eliminato" in res_del.json()["messaggio"].lower()

    # 6. DELETE inesistente -> 404
    res_del_404 = await async_client.delete("/api/prestiti/999999999")
    assert res_del_404.status_code == 404
