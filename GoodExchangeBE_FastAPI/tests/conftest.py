"""
Configurazione fixtures pytest condivise per tutti i test.

Architettura test (SRS §NFR-02):
- Unit test: usano AsyncMock per isolare DAO e service (nessun DB reale)
- Integration test: usano un DB PostgreSQL reale (goodexchange_test)
  con un client ASGI httpx che bypassa il network layer

SETUP TEST DB LOCALE:
    createdb goodexchange_test
    psql goodexchange_test < schema.sql
    export TEST_DATABASE_URL=postgresql://localhost/goodexchange_test
"""

import os
import uuid
from collections.abc import AsyncGenerator
from typing import Any

import asyncpg
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.main import app

# ——————————————————————————————————————————————
# Configurazione
# ——————————————————————————————————————————————

TEST_DB_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://localhost/goodexchange_test",
)


# ——————————————————————————————————————————————
# Fixtures per Integration Test
# ——————————————————————————————————————————————


@pytest_asyncio.fixture(scope="function")
async def db_pool() -> AsyncGenerator[asyncpg.Pool, None]:
    """
    Pool di connessioni asyncpg per il DB di test.
    Scope function: un pool per test garantisce isolamento dell'event loop.
    """
    pool = await asyncpg.create_pool(dsn=TEST_DB_URL, min_size=1, max_size=3)
    yield pool
    await pool.close()


@pytest_asyncio.fixture
async def db_conn(db_pool: asyncpg.Pool) -> AsyncGenerator[asyncpg.Connection, None]:
    """
    Connessione singola con rollback automatico al termine del test.
    Garantisce l'isolamento tra test senza necessità di cleanup manuale.
    """
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            yield conn
            # Il rollback automatico resetta il DB allo stato pre-test


@pytest_asyncio.fixture
async def async_client(db_pool: asyncpg.Pool) -> AsyncGenerator[AsyncClient, None]:
    """
    Client HTTP ASGI (httpx) per i test di integrazione delle API.
    Inietta il pool di test nell'app, senza avviare un server reale.
    """
    app.state.db_pool = db_pool
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


# ——————————————————————————————————————————————
# Dati di test condivisi
# ——————————————————————————————————————————————

UTENTE_TEST_BASE = {
    "username": "test_user_pytest",
    "password": "password_test",
    "nome": "Test",
    "cognome": "Utente",
    "codice_fiscale": "TSTUTS80A01H501X",
    "regione": "Emilia-Romagna",
    "provincia": "FE",
    "citta": "Ferrara",
    "via": "Via Roma",
    "civico": "1",
    "ruolo": "utente",
}


# ——————————————————————————————————————————————
# Fixtures dedicate per scenari complessi (FSM, ACID, Interazione tra entità)
# ——————————————————————————————————————————————


@pytest_asyncio.fixture
async def utente_proprietario(async_client: AsyncClient) -> dict[str, Any]:
    """Crea e restituisce un utente completo (ruolo 'utente' o 'proprietario') persistito nel DB di test."""
    username = f"prop_{uuid.uuid4().hex[:8]}"
    cf = f"PRP{uuid.uuid4().hex[:13].upper()}"[:16]
    payload = {**UTENTE_TEST_BASE, "username": username, "codice_fiscale": cf}
    res = await async_client.post("/api/utenti", json=payload)
    assert res.status_code == 201, f"Errore creazione proprietario: {res.text}"
    return res.json()


@pytest_asyncio.fixture
async def utente_beneficiario(async_client: AsyncClient) -> dict[str, Any]:
    """Crea e restituisce un secondo utente indipendente dal proprietario, persistito nel DB di test."""
    username = f"ben_{uuid.uuid4().hex[:8]}"
    cf = f"BEN{uuid.uuid4().hex[:13].upper()}"[:16]
    payload = {**UTENTE_TEST_BASE, "username": username, "codice_fiscale": cf}
    res = await async_client.post("/api/utenti", json=payload)
    assert res.status_code == 201, f"Errore creazione beneficiario: {res.text}"
    return res.json()


@pytest_asyncio.fixture
async def categoria_test(async_client: AsyncClient) -> dict[str, Any]:
    """Crea e restituisce una categoria di test con crediti impostati."""
    nome_cat = f"Cat_{uuid.uuid4().hex[:6]}"
    payload = {"nome": nome_cat, "crediti": 15, "descrizione": "Categoria per integration test"}
    res = await async_client.post("/api/categorie", json=payload)
    assert res.status_code == 201, f"Errore creazione categoria: {res.text}"
    return res.json()


@pytest_asyncio.fixture
async def bene_test(
    async_client: AsyncClient,
    utente_proprietario: dict[str, Any],
    categoria_test: dict[str, Any],
) -> dict[str, Any]:
    """Crea e restituisce un bene disponibile associato a proprietario e categoria preesistenti."""
    nome_bene = f"Bene_{uuid.uuid4().hex[:6]}"
    payload = {
        "nome": nome_bene,
        "descrizione": "Descrizione bene test integration",
        "id_categoria": categoria_test["id"],
        "id_proprietario": utente_proprietario["id"],
        "stato": True,
        "peso": 1.5,
    }
    res = await async_client.post("/api/beni", json=payload)
    assert res.status_code == 201, f"Errore creazione bene: {res.text}"
    return res.json()
