"""Test unitari isolati per Prestito DAO."""

from datetime import date
from unittest.mock import AsyncMock

import pytest

from src.dao import prestito_dao


@pytest.mark.asyncio
async def test_find_prestiti():
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = [
        {"id": 1, "stato": "richiesto", "bene_nome": "Trapano"}
    ]

    res = await prestito_dao.find_prestiti(
        mock_conn, {"stato": "richiesto", "id_beneficiario": 5}
    )
    assert len(res) == 1
    assert res[0]["bene_nome"] == "Trapano"
    mock_conn.fetch.assert_called_once()
    args = mock_conn.fetch.call_args[0]
    assert "WHERE p.stato = $1 AND p.id_beneficiario = $2" in args[0]
    assert args[1] == "richiesto"
    assert args[2] == 5


@pytest.mark.asyncio
async def test_find_prestito_by_id():
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": 10, "id_bene": 2, "stato": "accettato"}

    res = await prestito_dao.find_prestito_by_id(mock_conn, 10)
    assert res is not None
    assert res["id"] == 10
    assert res["stato"] == "accettato"
    mock_conn.fetchrow.assert_called_once_with(
        pytest.approx(mock_conn.fetchrow.call_args[0][0]), 10
    )


@pytest.mark.asyncio
async def test_verifica_disponibilita():
    mock_conn = AsyncMock()
    mock_conn.fetchval.return_value = 0

    res = await prestito_dao.verifica_disponibilita(
        mock_conn, 1, date(2026, 7, 10), date(2026, 7, 15)
    )
    assert res is True
    mock_conn.fetchval.assert_called_once()


@pytest.mark.asyncio
async def test_verifica_disponibilita_conflitto():
    mock_conn = AsyncMock()
    mock_conn.fetchval.return_value = 1

    res = await prestito_dao.verifica_disponibilita(
        mock_conn, 1, date(2026, 7, 10), date(2026, 7, 15)
    )
    assert res is False


@pytest.mark.asyncio
async def test_get_calendario_bene():
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = [
        {
            "data_inizio": date(2026, 7, 1),
            "data_fine": date(2026, 7, 5),
            "stato": "accettato",
            "beneficiario_username": "mario",
        }
    ]

    res = await prestito_dao.get_calendario_bene(mock_conn, 1, 2026, 7)
    assert len(res) == 1
    assert res[0]["beneficiario_username"] == "mario"
    mock_conn.fetch.assert_called_once()


@pytest.mark.asyncio
async def test_delete_prestito():
    mock_conn = AsyncMock()
    mock_conn.execute.return_value = "DELETE 1"

    success = await prestito_dao.delete_prestito(mock_conn, 10)
    assert success is True
    mock_conn.execute.assert_called_once_with("DELETE FROM prestito WHERE id = $1", 10)
