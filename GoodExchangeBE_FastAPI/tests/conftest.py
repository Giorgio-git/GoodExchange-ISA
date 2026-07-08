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
from collections.abc import AsyncGenerator

import asyncpg
import pytest
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


@pytest.fixture(scope="function")
async def db_pool() -> AsyncGenerator[asyncpg.Pool, None]:
    """
    Pool di connessioni asyncpg per il DB di test.
    Scope function: un pool per test garantisce isolamento dell'event loop.
    """
    pool = await asyncpg.create_pool(dsn=TEST_DB_URL, min_size=1, max_size=3)
    yield pool
    await pool.close()


@pytest.fixture
async def db_conn(db_pool: asyncpg.Pool) -> AsyncGenerator[asyncpg.Connection, None]:
    """
    Connessione singola con rollback automatico al termine del test.
    Garantisce l'isolamento tra test senza necessità di cleanup manuale.
    """
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            yield conn
            # Il rollback automatico resetta il DB allo stato pre-test


@pytest.fixture
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
