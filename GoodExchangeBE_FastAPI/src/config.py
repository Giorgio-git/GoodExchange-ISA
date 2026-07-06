"""
Configurazione centralizzata del progetto GoodExchange Backend.
Legge le variabili di ambiente dal file .env tramite pydantic-settings.
Corrisponde a config.js nel backend Node.js originale.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Impostazioni dell'applicazione caricate da variabili di ambiente."""

    pghost: str = "localhost"
    pgport: int = 5432
    pgdatabase: str = "GoodExchange"
    pguser: str = "postgres"
    pgpassword: str = "postgres"
    cors_origin: str = "http://localhost:4200"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Istanza singleton delle impostazioni — importata da tutti i moduli
settings = Settings()
