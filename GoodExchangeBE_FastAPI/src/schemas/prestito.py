"""
Schemi Pydantic per l'entità Prestito.
Include il validatore per le date e l'enum degli stati (FSM).
"""

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, model_validator

# Enum degli stati validi della FSM del prestito (Sezione 2.5 del contesto)
STATI_VALIDI = Literal[
    "richiesto", "accettato", "in_corso", "completato", "rifiutato", "annullato"
]


class PrestitoCreate(BaseModel):
    """Payload per la creazione di un prestito (POST /api/prestiti)."""

    id_bene: int
    id_beneficiario: int
    id_proprietario: int
    data_inizio: date
    data_fine: date
    stato: STATI_VALIDI = "richiesto"

    @model_validator(mode="after")
    def check_date_valide(self) -> "PrestitoCreate":
        """
        Precondizione (Design by Contract — Sezione 3.3):
        data_fine deve essere strettamente successiva a data_inizio.
        """
        if self.data_fine <= self.data_inizio:
            raise ValueError("data_fine deve essere successiva a data_inizio")
        return self


class PrestitoRead(BaseModel):
    """Risposta per la lettura di un prestito con dati JOIN."""

    id: int
    id_bene: int
    id_proprietario: int
    id_beneficiario: int
    data_inizio: date
    data_fine: date
    stato: str
    data: Optional[datetime] = None
    bene_nome: Optional[str] = None
    beneficiario_username: Optional[str] = None
    proprietario_username: Optional[str] = None

    model_config = {"from_attributes": True}


class StatoPrestitoUpdate(BaseModel):
    """Payload per l'aggiornamento dello stato del prestito (PUT /api/prestiti/:id/stato)."""

    stato: STATI_VALIDI


class DisponibilitaResponse(BaseModel):
    """Risposta per la verifica disponibilità bene."""

    disponibile: bool
