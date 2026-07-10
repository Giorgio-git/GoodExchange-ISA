"""Test unitari isolati per Preferiti DAO e PreferitiItem DAO."""

from unittest.mock import AsyncMock

import pytest

from src.dao import preferiti_dao, preferiti_item_dao


@pytest.mark.asyncio
async def test_find_preferiti_by_utente():
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": 1, "id_utente": 10}

    res = await preferiti_dao.find_preferiti_by_utente(mock_conn, 10)
    assert res is not None
    assert res["id_utente"] == 10
    mock_conn.fetchrow.assert_called_once_with(
        "SELECT * FROM preferiti WHERE id_utente=$1", 10
    )


@pytest.mark.asyncio
async def test_create_preferiti():
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": 1}

    res = await preferiti_dao.create_preferiti(mock_conn, 10, None)
    assert res is True
    mock_conn.fetchrow.assert_called_once()


@pytest.mark.asyncio
async def test_delete_preferiti():
    mock_conn = AsyncMock()
    mock_conn.execute.return_value = "DELETE 1"

    res = await preferiti_dao.delete_preferiti(mock_conn, 10)
    assert res is True
    mock_conn.execute.assert_called_once_with(
        "DELETE FROM preferiti WHERE id_utente=$1", 10
    )


@pytest.mark.asyncio
async def test_get_utenti_preferiti():
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = [{"id": 1, "id_utente_preferito": 5}]

    res = await preferiti_item_dao.get_utenti_preferiti(mock_conn, 1)
    assert len(res) == 1
    assert res[0]["id_utente_preferito"] == 5


@pytest.mark.asyncio
async def test_add_utente_preferito():
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": 1}

    res = await preferiti_item_dao.add_utente_preferito(mock_conn, 1, 5)
    assert res is True


@pytest.mark.asyncio
async def test_remove_utente_preferito():
    mock_conn = AsyncMock()
    mock_conn.execute.return_value = "DELETE 1"

    res = await preferiti_item_dao.remove_utente_preferito(mock_conn, 1, 5)
    assert res is True
