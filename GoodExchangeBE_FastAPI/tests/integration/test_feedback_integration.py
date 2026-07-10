import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_feedback_creazione_e_ricalcolo_reputazione_integration(
    async_client: AsyncClient,
    utente_proprietario: dict,
    utente_beneficiario: dict,
):
    """
    Verifica che la creazione di un feedback aggiorni dinamicamente la reputazione del destinatario
    (integrazione Three-Tier tramite feedback_service).
    """
    id_mittente = utente_proprietario["id"]
    id_destinatario = utente_beneficiario["id"]
    username_destinatario = utente_beneficiario["username"]

    payload = {
        "id_utente": id_mittente,
        "id_destinatario": id_destinatario,
        "voto": 5,
    }

    # 1. Creazione Feedback (POST /api/feedback)
    res_create = await async_client.post("/api/feedback", json=payload)
    assert res_create.status_code == 201

    # 2. Verifica che la reputazione del destinatario sia stata aggiornata al voto (o media voti)
    res_dest = await async_client.get(f"/api/utenti/{id_destinatario}")
    assert res_dest.status_code == 200
    reputazione_aggiornata = res_dest.json().get("reputazione")
    assert reputazione_aggiornata is not None
    assert float(reputazione_aggiornata) == pytest.approx(5.0)

    # 3. Lettura per username (GET /api/feedback/username/:username)
    res_get_username = await async_client.get(
        f"/api/feedback/username/{username_destinatario}"
    )
    assert res_get_username.status_code == 200
    assert any(f["voto"] == 5 for f in res_get_username.json())


@pytest.mark.asyncio
async def test_feedback_validazione_dbc_integration(
    async_client: AsyncClient,
    utente_proprietario: dict,
    utente_beneficiario: dict,
):
    """Verifica le precondizioni DbC di Pydantic e del DB (voto out of range e auto-feedback)."""
    # 1. Voto fuori range -> 422 Unprocessable Entity
    payload_invalid_voto = {
        "id_utente": utente_proprietario["id"],
        "id_destinatario": utente_beneficiario["id"],
        "voto": 10,
    }
    res_voto = await async_client.post("/api/feedback", json=payload_invalid_voto)
    assert res_voto.status_code == 422

    # 2. Auto-feedback (id_utente == id_destinatario) -> 422 Unprocessable Entity
    payload_auto = {
        "id_utente": utente_proprietario["id"],
        "id_destinatario": utente_proprietario["id"],
        "voto": 4,
    }
    res_auto = await async_client.post("/api/feedback", json=payload_auto)
    assert res_auto.status_code == 422
