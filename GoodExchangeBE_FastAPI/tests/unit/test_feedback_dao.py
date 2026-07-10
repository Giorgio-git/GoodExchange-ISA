"""Test unitari isolati per Feedback DAO."""

from unittest.mock import AsyncMock

import pytest

from src.dao import feedback_dao


@pytest.mark.asyncio
async def test_find_feedback_by_user_id():
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = [{"id": 1, "id_destinatario": 10, "voto": 5}]

    res = await feedback_dao.find_feedback_by_user_id(mock_conn, 10)
    assert len(res) == 1
    assert res[0]["voto"] == 5


@pytest.mark.asyncio
async def test_find_feedback_by_username():
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": 10}
    mock_conn.fetch.return_value = [{"id": 1, "id_destinatario": 10, "voto": 4}]

    res = await feedback_dao.find_feedback_by_username(mock_conn, "giorgio")
    assert len(res) == 1
    assert res[0]["voto"] == 4
    mock_conn.fetchrow.assert_called_once_with(
        "SELECT id FROM utente WHERE username=$1", "giorgio"
    )


@pytest.mark.asyncio
async def test_find_feedback_by_username_not_found():
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = None

    res = await feedback_dao.find_feedback_by_username(mock_conn, "inesistente")
    assert res == []


@pytest.mark.asyncio
async def test_create_feedback():
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": 100}

    payload = {"id_utente": 1, "id_destinatario": 2, "voto": 5, "data": "2026-07-09"}
    res = await feedback_dao.create_feedback(mock_conn, payload)
    assert res is not None
    assert res["id"] == 100
    assert res["voto"] == 5


@pytest.mark.asyncio
async def test_delete_feedback():
    mock_conn = AsyncMock()
    mock_conn.execute.return_value = "DELETE 1"

    res = await feedback_dao.delete_feedback(mock_conn, 100)
    assert res is True


@pytest.mark.asyncio
async def test_calcola_reputazione_media():
    mock_conn = AsyncMock()
    mock_conn.fetchval.return_value = 4.5

    res = await feedback_dao.calcola_reputazione_media(mock_conn, 2)
    assert res == 4.5
    mock_conn.fetchval.assert_called_once()
