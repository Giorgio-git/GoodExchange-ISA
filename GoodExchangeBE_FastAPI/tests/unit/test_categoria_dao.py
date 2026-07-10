"""Test unitari isolati per Categoria DAO."""

from unittest.mock import AsyncMock

import pytest

from src.dao import categoria_dao


@pytest.mark.asyncio
async def test_find_categorie():
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = [
        {
            "id": 1,
            "nome": "Elettronica",
            "crediti": 10,
            "descrizione": "Gadget e strumenti",
        },
        {
            "id": 2,
            "nome": "Fai da te",
            "crediti": 5,
            "descrizione": "Attrezzi da lavoro",
        },
    ]

    res = await categoria_dao.find_categorie(mock_conn)
    assert len(res) == 2
    assert res[0]["nome"] == "Elettronica"
    assert res[1]["crediti"] == 5
    mock_conn.fetch.assert_called_once_with("SELECT * FROM categoria ORDER BY nome ASC")


@pytest.mark.asyncio
async def test_find_categoria_by_id():
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": 1, "nome": "Elettronica", "crediti": 10}

    res = await categoria_dao.find_categoria_by_id(mock_conn, 1)
    assert res is not None
    assert res["nome"] == "Elettronica"
    mock_conn.fetchrow.assert_called_once_with("SELECT * FROM categoria WHERE id=$1", 1)


@pytest.mark.asyncio
async def test_find_categoria_by_id_not_found():
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = None

    res = await categoria_dao.find_categoria_by_id(mock_conn, 999)
    assert res is None


@pytest.mark.asyncio
async def test_create_categoria():
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": 15}

    payload = {"nome": "Sport", "crediti": 20, "descrizione": "Attrezzatura sportiva"}
    res = await categoria_dao.create_categoria(mock_conn, payload)
    assert res is not None
    assert res["id"] == 15
    assert res["nome"] == "Sport"
    mock_conn.fetchrow.assert_called_once()


@pytest.mark.asyncio
async def test_update_categoria():
    mock_conn = AsyncMock()
    mock_conn.execute.return_value = "UPDATE 1"

    aggiornamenti = {"crediti": 25, "descrizione": "Nuova descrizione"}
    success = await categoria_dao.update_categoria(mock_conn, 1, aggiornamenti)
    assert success is True
    call_args = mock_conn.execute.call_args[0]
    assert "UPDATE categoria SET" in call_args[0]
    assert call_args[1] == 25
    assert call_args[2] == "Nuova descrizione"
    assert call_args[3] == 1


@pytest.mark.asyncio
async def test_delete_categoria():
    mock_conn = AsyncMock()
    mock_conn.execute.return_value = "DELETE 1"

    success = await categoria_dao.delete_categoria(mock_conn, 1)
    assert success is True
    mock_conn.execute.assert_called_once_with("DELETE FROM categoria WHERE id = $1", 1)
