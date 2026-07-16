"""Schemi Pydantic per le entità Feedback, Messaggio, Recensione, Segnalazione, Suggerimento, Preferiti."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator

# ——— Feedback ———


class FeedbackCreate(BaseModel):
    id_utente: int
    id_destinatario: int
    voto: int  # 1–5 (CHECK nel DB)
    data: Optional[datetime] = None

    @field_validator("voto")
    @classmethod
    def check_voto_valido(cls, v: int) -> int:
        """
        Pre-condizione DbC:
        il voto deve essere un intero nel range [1, 5].
        """
        if v < 1 or v > 5:
            raise ValueError("Il voto deve essere compreso tra 1 e 5")
        return v

    @model_validator(mode="after")
    def check_utenti_diversi(self) -> "FeedbackCreate":
        """
        Pre-condizione DbC:
        l'utente non può lasciare un feedback a se stesso.
        """
        if self.id_utente == self.id_destinatario:
            raise ValueError("Non puoi lasciare un feedback a te stesso")
        return self


class FeedbackRead(BaseModel):
    id: int
    id_utente: int
    id_destinatario: int
    voto: int
    data: Optional[datetime] = None

    model_config = {"from_attributes": True}
