"""Schemi Pydantic per l'entità Messaggio."""

from typing import Literal

from pydantic import BaseModel

TIPI_MESSAGGIO = Literal[
    "prestito", "recensione", "segnalazione", "feedback", "suggerimento"
]


class MessaggioCreate(BaseModel):
    id_mittente: int
    id_destinatario: int
    titolo: str = "senza titolo"
    contenuto: str
    tipo: TIPI_MESSAGGIO
    id_riferito: int


class MessaggioRead(BaseModel):
    id: int
    id_mittente: int
    id_destinatario: int
    titolo: str
    contenuto: str
    tipo: str
    id_riferito: int

    model_config = {"from_attributes": True}
