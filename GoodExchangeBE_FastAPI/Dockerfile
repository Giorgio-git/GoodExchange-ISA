# ——— STAGE 1: Build & Dependencies ———
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Copia i manifest delle dipendenze (e il lockfile) per sfruttare la cache dei layer Docker
COPY pyproject.toml uv.lock ./

# Installazione dipendenze in un virtualenv isolato in /app/.venv
RUN uv sync --frozen --no-install-project --no-dev

# Copia del codice sorgente
COPY src/ /app/src/

# Installazione del pacchetto principale
RUN uv sync --frozen --no-dev


# ——— STAGE 2: Runtime Minimal ———
FROM python:3.11-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Creazione utente non-root per la sicurezza (Sezione 6.x)
RUN groupadd -r goodexchange && useradd -r -g goodexchange -d /app -s /sbin/nologin goodexchange

# Copia del virtualenv e del codice dallo stage builder
COPY --from=builder --chown=goodexchange:goodexchange /app/.venv /app/.venv
COPY --from=builder --chown=goodexchange:goodexchange /app/src /app/src

USER goodexchange

EXPOSE 3000

ENTRYPOINT ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "3000"]
