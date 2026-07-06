"""Schemi Pydantic per l'entità Bene."""

from typing import Optional

from pydantic import BaseModel


class BeneCreate(BaseModel):
    """Payload per la creazione di un bene (POST /api/beni)."""

    id_proprietario: int
    id_categoria: int
    nome: str
    descrizione: Optional[str] = None
    peso: Optional[float] = None
    stato: Optional[bool] = None


class BeneRead(BaseModel):
    """Risposta per la lettura di un bene — esclude il campo immagine (BYTEA)."""

    id: int
    id_proprietario: int
    id_categoria: int
    nome: str
    descrizione: Optional[str] = None
    peso: Optional[float] = None
    stato: Optional[bool] = None

    model_config = {"from_attributes": True}


class BeneUpdate(BaseModel):
    """Payload per l'aggiornamento parziale di un bene (PUT /api/beni/:id)."""

    id_categoria: Optional[int] = None
    nome: Optional[str] = None
    descrizione: Optional[str] = None
    peso: Optional[float] = None
    stato: Optional[bool] = None
