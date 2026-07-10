"""Test unitari isolati per Segnalazione DAO."""

from unittest.mock import AsyncMock

import pytest

from src.dao import segnalazione_dao


@pytest.mark.asyncio
async def test_create_segnalazione():
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": 10}

    payload = {"id_segnalante": 1, "id_segnalato": 2, "stato": "aperta"}
    res = await segnalazione_dao.create_segnalazione(mock_conn, payload)
    assert res is not None
    assert res["id"] == 10
    mock_conn.fetchrow.assert_called_once()
    args = mock_conn.fetchrow.call_args[0]
    assert "INSERT INTO segnalazione" in args[0]
    assert args[1] == 1
    assert args[2] == 2
    assert args[3] == "aperta"


@pytest.mark.asyncio
async def test_find_segnalazioni():
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = [{"id": 10, "stato": "aperta"}]

    res = await segnalazione_dao.find_segnalazioni(mock_conn, {"stato": "aperta"})
    assert len(res) == 1
    assert res[0]["stato"] == "aperta"
    mock_conn.fetch.assert_called_once()
    args = mock_conn.fetch.call_args[0]
    assert "WHERE stato = $1" in args[0]
    assert args[1] == "aperta"


@pytest.mark.asyncio
async def test_find_segnalazione_by_id():
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": 10, "id_segnalante": 1}

    res = await segnalazione_dao.find_segnalazione_by_id(mock_conn, 10)
    assert res is not None
    assert res["id"] == 10
    mock_conn.fetchrow.assert_called_once_with(
        "SELECT * FROM segnalazione WHERE id=$1", 10
    )


@pytest.mark.asyncio
async def test_update_segnalazione_stato():
    mock_conn = AsyncMock()
    mock_conn.execute.return_value = "UPDATE 1"

    success = await segnalazione_dao.update_segnalazione_stato(mock_conn, 10, "risolta")
    assert success is True
    mock_conn.execute.assert_called_once_with(
        "UPDATE segnalazione SET stato=$1 WHERE id=$2", "risolta", 10
    )
