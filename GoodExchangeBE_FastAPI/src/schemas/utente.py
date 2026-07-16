"""
Schemi Pydantic per l'entità Utente.
Usati per validazione input e serializzazione output nelle API.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


class UtenteCreate(BaseModel):
    """Payload per la creazione di un nuovo utente (POST /api/utenti)."""

    username: str
    password: str
    nome: str
    cognome: str
    codice_fiscale: str
    regione: str
    provincia: str
    citta: str
    via: str
    civico: str
    ruolo: Literal["admin", "utente"] = "utente"


class UtenteRead(BaseModel):
    """Risposta per lettura utente — esclude la password per sicurezza."""

    id: int
    username: str
    nome: str
    cognome: str
    codice_fiscale: str
    regione: str
    provincia: str
    citta: str
    via: str
    civico: str
    ruolo: str
    stato: str
    crediti_valore_beni: int
    crediti_accumulati: int
    cauzione: float
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UtenteLogin(BaseModel):
    """Payload per l'autenticazione (POST /api/utenti/login)."""

    username: str
    password: str


class UtenteUpdate(BaseModel):
    """Payload per l'aggiornamento dinamico di un utente (PUT /api/utenti/:id)."""

    nome: Optional[str] = None
    cognome: Optional[str] = None
    password: Optional[str] = None
    regione: Optional[str] = None
    provincia: Optional[str] = None
    citta: Optional[str] = None
    via: Optional[str] = None
    civico: Optional[str] = None
    ruolo: Optional[Literal["admin", "utente"]] = None


class StatoUpdate(BaseModel):
    """Payload per l'aggiornamento dello stato utente."""

    stato: Literal["attivo", "disattivo"]


class CauzioneUpdate(BaseModel):
    """Payload per l'aggiornamento della cauzione utente."""

    cauzione: float


class CreditiResponse(BaseModel):
    """Risposta per il calcolo dei crediti utente."""

    crediti_valore_beni: int
    crediti_accumulati: int
