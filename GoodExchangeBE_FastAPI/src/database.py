"""
Gestione del pool di connessioni asyncpg.
Equivalente a services/db.js nel backend Node.js originale.

Principio Clean Code (Sezione 4.3 del contesto):
- Vietato aprire connessioni senza chiusura esplicita.
- Utilizzo obbligatorio del Context Manager 'async with' per garantire
  la restituzione della connessione al pool al termine della richiesta.
"""

from collections.abc import AsyncGenerator

import asyncpg
from fastapi import Request

from src.config import settings


async def create_db_pool() -> asyncpg.Pool:
    """
    Crea e restituisce il pool di connessioni asyncpg.
    Chiamato una sola volta durante il lifespan dell'applicazione (startup).
    """
    return await asyncpg.create_pool(
        host=settings.pghost,
        port=settings.pgport,
        database=settings.pgdatabase,
        user=settings.pguser,
        password=settings.pgpassword,
        min_size=2,
        max_size=10,
    )


async def get_connection(
    request: Request,
) -> AsyncGenerator[asyncpg.Connection, None]:
    """
    FastAPI Dependency che fornisce una connessione dal pool.
    Il context manager garantisce il rilascio automatico al pool
    al termine di ogni richiesta HTTP, anche in caso di eccezione.

    Uso:
        conn: asyncpg.Connection = Depends(get_connection)
    """
    async with request.app.state.db_pool.acquire() as connection:
        yield connection
