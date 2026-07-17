"""
Router FastAPI per Feedback.
ORDINE: /username/:username PRIMA di /:id per evitare conflitti.

ARCHITETTURA (Three-Tier):
  La creazione di un feedback delega al service layer per aggiornare
  atomicamente la reputazione del destinatario.
"""

import asyncpg
from fastapi import APIRouter, Depends, HTTPException

from src.dao import feedback_dao
from src.database import get_connection
from src.schemas.feedback import FeedbackCreate
from src.services import feedback_service

router = APIRouter(tags=["Feedback"])


# PRIMA di /{id}
@router.get("/feedback/username/{username}")
async def get_feedback_by_username(
    username: str, conn: asyncpg.Connection = Depends(get_connection)
):
    """Feedback per username."""
    async with conn.transaction():
        feedback = await feedback_dao.find_feedback_by_username(conn, username)
        if not feedback:
            raise HTTPException(
                status_code=404, detail="Nessun feedback trovato per questo utente"
            )
        return feedback


@router.get("/feedback/{id}")
async def get_feedback_by_user_id(
    id: int, conn: asyncpg.Connection = Depends(get_connection)
):
    """Feedback per ID utente."""
    async with conn.transaction():
        feedback = await feedback_dao.find_feedback_by_user_id(conn, id)
        if not feedback:
            raise HTTPException(
                status_code=404, detail="Nessun feedback trovato per questo utente"
            )
        return feedback


@router.post("/feedback", status_code=201)
async def create_feedback(
    feedback: FeedbackCreate, conn: asyncpg.Connection = Depends(get_connection)
):
    """
    Crea feedback e aggiorna la reputazione media del destinatario.

    Delega al service layer (feedback_service) per incapsulare la logica
    di business: creazione feedback + ricalcolo reputazione atomico.
    """
    async with conn.transaction():
        result = await feedback_service.crea_feedback_e_aggiorna_reputazione(
            conn, feedback.model_dump()
        )
        if not result:
            raise HTTPException(status_code=400, detail="Creazione feedback fallita")
        return result


@router.delete("/feedback/{id}")
async def delete_feedback(id: int, conn: asyncpg.Connection = Depends(get_connection)):
    """Elimina feedback (solo admin)."""
    async with conn.transaction():
        result = await feedback_dao.delete_feedback(conn, id)
        if not result:
            raise HTTPException(
                status_code=404, detail="Feedback non trovato o non eliminato"
            )
        return {"messaggio": "Feedback eliminato con successo"}
