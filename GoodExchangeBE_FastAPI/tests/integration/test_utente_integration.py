import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import UTENTE_TEST_BASE


@pytest.mark.asyncio
async def test_creazione_e_lettura_utente_integration(async_client: AsyncClient):
    """
    Verifica il flusso completo di registrazione utente e lettura.
    Usa username univoco (uuid4) per rendere il test idempotente su più esecuzioni.
    """
    unique_username = f"int_test_{uuid.uuid4().hex[:8]}"
    unique_cf = f"TST{uuid.uuid4().hex[:13].upper()}"[:16]
    payload = {**UTENTE_TEST_BASE, "username": unique_username, "codice_fiscale": unique_cf}

    # 1. Creazione (POST)
    res_create = await async_client.post("/api/utenti", json=payload)
    assert res_create.status_code == 201
    data_create = res_create.json()
    assert data_create["username"] == unique_username
    assert "password" not in data_create  # Sicurezza: la password non deve mai tornare! (SRS §NFR-05)

    id_generato = data_create.get("id") or data_create.get("id_utente")

    # 2. Lettura per username (GET /api/utenti/username/:username)
    res_read_user = await async_client.get(f"/api/utenti/username/{unique_username}")
    assert res_read_user.status_code == 200
    assert res_read_user.json()["username"] == unique_username

    # 3. Lettura per ID (GET /api/utenti/:id)
    if id_generato:
        res_read_id = await async_client.get(f"/api/utenti/{id_generato}")
        assert res_read_id.status_code == 200
        assert res_read_id.json()["nome"] == "Test"


@pytest.mark.asyncio
async def test_login_successo_integration(async_client: AsyncClient):
    """Verifica che un utente appena creato possa fare login con successo e che la password non sia esposta."""
    unique_username = f"log_{uuid.uuid4().hex[:8]}"
    unique_cf = f"LOG{uuid.uuid4().hex[:13].upper()}"[:16]
    payload = {**UTENTE_TEST_BASE, "username": unique_username, "codice_fiscale": unique_cf, "password": "SegretaPassword123"}

    res_create = await async_client.post("/api/utenti", json=payload)
    assert res_create.status_code == 201

    res_login = await async_client.post(
        "/api/utenti/login",
        json={"username": unique_username, "password": "SegretaPassword123"},
    )
    assert res_login.status_code == 200
    login_data = res_login.json()
    assert login_data["messaggio"] == "Login effettuato con successo"
    assert login_data["utente"]["username"] == unique_username
    assert "password" not in login_data["utente"]


@pytest.mark.asyncio
async def test_login_fallito_integration(async_client: AsyncClient):
    """Verifica che credenziali errate restituiscano 401 Unauthorized."""
    res = await async_client.post(
        "/api/utenti/login",
        json={"username": "inesistente", "password": "err"},
    )
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_aggiornamento_stato_e_cauzione_integration(async_client: AsyncClient, utente_proprietario: dict):
    """Verifica la modifica dinamica dello stato e della cauzione dell'utente (test di integrazione su chiamate PUT)."""
    user_id = utente_proprietario["id"]

    # 1. Modifica stato in "disattivo"
    res_stato = await async_client.put(f"/api/utenti/{user_id}/stato", json={"stato": "disattivo"})
    assert res_stato.status_code == 200

    # 2. Modifica cauzione
    res_cauzione = await async_client.put(f"/api/utenti/{user_id}/cauzione", json={"cauzione": 150.50})
    assert res_cauzione.status_code == 200

    # 3. Verifica persistenza delle modifiche
    res_get = await async_client.get(f"/api/utenti/{user_id}")
    assert res_get.status_code == 200
    user_data = res_get.json()
    assert user_data["stato"] == "disattivo"
    assert float(user_data["cauzione"]) == pytest.approx(150.50)


@pytest.mark.asyncio
async def test_creazione_utente_duplicato_integration(async_client: AsyncClient, utente_proprietario: dict):
    """Verifica che tentare di creare un utente con username duplicato scateni un errore di vincolo nel database."""
    username_duplicato = utente_proprietario["username"]
    payload = {
        **UTENTE_TEST_BASE,
        "username": username_duplicato,
        "codice_fiscale": f"DUP{uuid.uuid4().hex[:13].upper()}"[:16],
    }
    # In assenza di cattura esplicita nel router/DAO per UniqueViolationError, l'eccezione si propaga o dà errore di server/database
    res = await async_client.post("/api/utenti", json=payload)
    assert res.status_code in (400, 409, 500)
