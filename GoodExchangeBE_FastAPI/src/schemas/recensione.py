"""Schemi Pydantic per Recensione, Segnalazione, Suggerimento e Preferiti."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

# ——— Recensione ———


class RecensioneCreate(BaseModel):
    id_bene: int
    id_beneficiario: int
    voto: int  # 1–5

    @field_validator("voto")
    @classmethod
    def check_voto_valido(cls, v: int) -> int:
        """Pre-condizione DbC: il voto deve essere un intero nel range [1, 5]."""
        if v < 1 or v > 5:
            raise ValueError("Il voto deve essere compreso tra 1 e 5")
        return v


class RecensioneRead(BaseModel):
    id: int
    id_bene: int
    id_beneficiario: int
    voto: int
    data: Optional[datetime] = None

    model_config = {"from_attributes": True}
