"""Schemi Pydantic per l'entità Categoria."""

from typing import Optional

from pydantic import BaseModel


class CategoriaCreate(BaseModel):
    nome: str
    crediti: int = 0
    descrizione: Optional[str] = None


class CategoriaRead(BaseModel):
    id: int
    nome: str
    crediti: int
    descrizione: Optional[str] = None

    model_config = {"from_attributes": True}


class CategoriaUpdate(BaseModel):
    nome: Optional[str] = None
    crediti: Optional[int] = None
    descrizione: Optional[str] = None
