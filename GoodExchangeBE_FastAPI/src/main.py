"""
Entry point dell'applicazione FastAPI GoodExchange Backend.
Equivalente a app.js nel backend Node.js originale.

Architettura Three-Tier (Sezione 2.6 del contesto):
    FastAPI Routers (Presentation)
        --USES-->
    Business Services (Logic)
        --USES-->
    DAO Modules (Data Access)
"""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.database import create_db_pool
from src.routers import (
    bene_router,
    categoria_router,
    feedback_router,
    messaggio_router,
    preferiti_item_router,
    preferiti_router,
    prestito_router,
    recensione_router,
    segnalazione_router,
    suggerimento_router,
    utente_router,
)

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestore del ciclo di vita dell'applicazione.
    Startup: crea il pool di connessioni asyncpg.
    Shutdown: chiude il pool e rilascia tutte le connessioni.
    """
    logger.info("Avvio GoodExchange Backend — creazione pool connessioni DB...")
    app.state.db_pool = await create_db_pool()
    logger.info("Pool connessioni DB creato con successo.")

    # Auto-Migrazione / Check dello schema al boot (Self-Healing del DB locale)
    async with app.state.db_pool.acquire() as conn:
        try:
            await conn.execute("""
                ALTER TABLE utente
                ADD COLUMN IF NOT EXISTS reputazione DECIMAL(3,2) DEFAULT NULL
                CHECK (reputazione IS NULL OR (reputazione >= 1.0 AND reputazione <= 5.0));
            """)
            logger.info(
                "Check/migrazione colonna 'reputazione' su tabella utente completato con successo."
            )
        except Exception as e_mig:
            logger.warning("Nota durante verifica schema reputazione: %s", e_mig)

    yield
    logger.info("Chiusura GoodExchange Backend — rilascio pool connessioni DB...")
    await app.state.db_pool.close()
    logger.info("Pool connessioni DB chiuso.")


# Creazione dell'app FastAPI con lifespan context manager
app = FastAPI(
    title="GoodExchange API",
    description="Backend transazionale per la piattaforma di scambio beni GoodExchange",
    version="1.0.0",
    lifespan=lifespan,
)


# ——— Middleware ———

# CORS: abilita il frontend Angular su http://localhost:4200
# Equivalente a: app.use(cors({ origin: 'http://localhost:4200' }))
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origin.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware di logging delle richieste HTTP
# Equivalente al middleware console.log in app.js
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    return response


# ——— Router — prefisso /api ———
# Equivalente a: app.use(contextPath, router)
API_PREFIX = "/api"

app.include_router(utente_router.router, prefix=API_PREFIX)
app.include_router(bene_router.router, prefix=API_PREFIX)
app.include_router(recensione_router.router, prefix=API_PREFIX)
app.include_router(feedback_router.router, prefix=API_PREFIX)
app.include_router(prestito_router.router, prefix=API_PREFIX)
app.include_router(categoria_router.router, prefix=API_PREFIX)
app.include_router(messaggio_router.router, prefix=API_PREFIX)
app.include_router(segnalazione_router.router, prefix=API_PREFIX)
app.include_router(suggerimento_router.router, prefix=API_PREFIX)
app.include_router(preferiti_router.router, prefix=API_PREFIX)
app.include_router(preferiti_item_router.router, prefix=API_PREFIX)


# ——— Handler 404 catch-all ———
# Equivalente a: app.all('*', function(req, res) { res.status(404).json(...) })
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"erroreMsg": "Risorsa non trovata"},
    )


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=3000,
        reload=False,
        log_level="info",
    )
