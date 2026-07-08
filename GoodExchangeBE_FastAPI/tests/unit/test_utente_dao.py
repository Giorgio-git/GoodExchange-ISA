"""Test unitari isolati per Utente DAO."""

from unittest.mock import AsyncMock

import pytest

from src.dao import utente_dao


@pytest.mark.asyncio
async def test_find_utente_by_username():
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {
        "id": 1,
        "username": "giobdock",
        "ruolo": "admin",
    }

    res = await utente_dao.find_utente_by_username(mock_conn, "giobdock")
    assert res is not None
    assert res["username"] == "giobdock"
    assert mock_conn.fetchrow.await_count == 2


@pytest.mark.asyncio
async def test_find_utenti_con_filtri():
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = [{"id": 1, "citta": "Ferrara"}]

    res = await utente_dao.find_utenti(mock_conn, {"citta": "Ferrara", "ruolo": None})
    assert len(res) == 1
    assert res[0]["citta"] == "Ferrara"
    # Accertarsi che la query contenga WHERE citta ILIKE $1 e ignori ruolo=None
    call_args = mock_conn.fetch.call_args[0]
    assert "WHERE citta ILIKE $1" in call_args[0]
    assert call_args[1] == "%Ferrara%"
