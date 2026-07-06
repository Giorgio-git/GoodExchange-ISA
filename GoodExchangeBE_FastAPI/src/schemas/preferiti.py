"""Schemi Pydantic per Preferiti e PreferitiItem."""

from pydantic import BaseModel


class PreferitiRead(BaseModel):
    id: int
    id_utente: int

    model_config = {"from_attributes": True}


class PreferitiItemRead(BaseModel):
    id: int
    id_utente_preferito: int

    model_config = {"from_attributes": True}
