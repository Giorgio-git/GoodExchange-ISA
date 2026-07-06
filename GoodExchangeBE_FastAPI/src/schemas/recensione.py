"""Schemi Pydantic per Recensione, Segnalazione, Suggerimento e Preferiti."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

# ——— Recensione ———


class RecensioneCreate(BaseModel):
    id_bene: int
    id_beneficiario: int
    voto: int  # 1–5


class RecensioneRead(BaseModel):
    id: int
    id_bene: int
    id_beneficiario: int
    voto: int
    data: Optional[datetime] = None

    model_config = {"from_attributes": True}
