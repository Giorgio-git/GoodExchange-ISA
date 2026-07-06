"""Schemi Pydantic per Suggerimento."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

STATI_SUGGERIMENTO = Literal["richiesto", "completato"]


class SuggerimentoCreate(BaseModel):
    id_mittente: int


class SuggerimentoRead(BaseModel):
    id: int
    id_mittente: int
    data: Optional[datetime] = None
    stato: str

    model_config = {"from_attributes": True}


class StatoSuggerimentoUpdate(BaseModel):
    stato: STATI_SUGGERIMENTO
