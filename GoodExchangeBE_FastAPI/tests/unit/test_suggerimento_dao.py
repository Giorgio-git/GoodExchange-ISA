"""Test unitari isolati per Suggerimento DAO."""

from unittest.mock import AsyncMock

import pytest

from src.dao import suggerimento_dao


@pytest.mark.asyncio
async def test_find_suggerimenti():
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = [{"id": 1, "stato": "richiesto"}]

    res = await suggerimento_dao.find_suggerimenti(mock_conn, {"stato": "richiesto"})
    assert len(res) == 1
    assert res[0]["stato"] == "richiesto"
    mock_conn.fetch.assert_called_once()
    args = mock_conn.fetch.call_args[0]
    assert "WHERE stato = $1" in args[0]
    assert args[1] == "richiesto"


@pytest.mark.asyncio
async def test_create_suggerimento():
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": 5, "id_mittente": 2, "stato": "richiesto"}

    res = await suggerimento_dao.create_suggerimento(mock_conn, {"id_mittente": 2})
    assert res is not None
    assert res["id"] == 5
    assert res["stato"] == "richiesto"
    mock_conn.fetchrow.assert_called_once()
    args = mock_conn.fetchrow.call_args[0]
    assert "INSERT INTO suggerimento" in args[0]
    assert args[1] == 2


@pytest.mark.asyncio
async def test_update_suggerimento_stato():
    mock_conn = AsyncMock()
    mock_conn.execute.return_value = "UPDATE 1"

    success = await suggerimento_dao.update_suggerimento_stato(
        mock_conn, 5, "completato"
    )
    assert success is True
    mock_conn.execute.assert_called_once_with(
        "UPDATE suggerimento SET stato=$1 WHERE id=$2", "completato", 5
    )
