"""Test unitari isolati per Recensione DAO."""

from unittest.mock import AsyncMock

import pytest

from src.dao import recensione_dao


@pytest.mark.asyncio
async def test_find_recensioni():
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = [{"id": 1, "voto": 5}]

    res = await recensione_dao.find_recensioni(mock_conn, {"id_bene": 10})
    assert len(res) == 1
    assert res[0]["voto"] == 5
    mock_conn.fetch.assert_called_once()
    args = mock_conn.fetch.call_args[0]
    assert "WHERE id_bene = $1" in args[0]
    assert args[1] == 10


@pytest.mark.asyncio
async def test_find_recensione_by_id():
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": 1, "voto": 4}

    res = await recensione_dao.find_recensione_by_id(mock_conn, 1)
    assert res is not None
    assert res["voto"] == 4
    mock_conn.fetchrow.assert_called_once_with(
        "SELECT * FROM recensione WHERE id=$1", 1
    )


@pytest.mark.asyncio
async def test_create_recensione():
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": 20}

    payload = {"id_bene": 5, "id_beneficiario": 3, "voto": 5}
    res = await recensione_dao.create_recensione(mock_conn, payload)
    assert res is not None
    assert res["id"] == 20
    assert res["voto"] == 5
    mock_conn.fetchrow.assert_called_once()


@pytest.mark.asyncio
async def test_update_recensione():
    mock_conn = AsyncMock()
    mock_conn.execute.return_value = "UPDATE 1"

    success = await recensione_dao.update_recensione(mock_conn, 1, {"voto": 3})
    assert success is True
    mock_conn.execute.assert_called_once()
    args = mock_conn.execute.call_args[0]
    assert "UPDATE recensione SET" in args[0]
    assert args[1] == 3


@pytest.mark.asyncio
async def test_delete_recensione():
    mock_conn = AsyncMock()
    mock_conn.execute.return_value = "DELETE 1"

    success = await recensione_dao.delete_recensione(mock_conn, 1)
    assert success is True
    mock_conn.execute.assert_called_once_with("DELETE FROM recensione WHERE id=$1", 1)
