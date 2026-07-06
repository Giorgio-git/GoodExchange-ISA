"""Schemi Pydantic per Segnalazione."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

STATI_SEGNALAZIONE = Literal["aperta", "in_gestione", "risolta", "respinta"]


class SegnalazioneCreate(BaseModel):
    id_segnalante: int
    id_segnalato: Optional[int] = None
    data: Optional[datetime] = None
    stato: STATI_SEGNALAZIONE = "aperta"


class SegnalazioneRead(BaseModel):
    id: int
    id_segnalante: int
    id_segnalato: Optional[int] = None
    data: Optional[datetime] = None
    stato: str

    model_config = {"from_attributes": True}


class StatoSegnalazioneUpdate(BaseModel):
    stato: STATI_SEGNALAZIONE
