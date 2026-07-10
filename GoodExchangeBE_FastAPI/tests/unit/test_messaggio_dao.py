"""Test unitari isolati per Messaggio DAO."""

from unittest.mock import AsyncMock

import pytest

from src.dao import messaggio_dao


@pytest.mark.asyncio
async def test_create_messaggio():
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": 100}

    payload = {
        "id_mittente": 1,
        "id_destinatario": 2,
        "titolo": "Ciao",
        "contenuto": "Contenuto del messaggio",
        "tipo": "comunicazione",
        "id_riferito": 10,
    }
    msg_id = await messaggio_dao.create_messaggio(mock_conn, payload)
    assert msg_id == 100
    mock_conn.fetchrow.assert_called_once()
    args = mock_conn.fetchrow.call_args[0]
    assert "INSERT INTO messaggio" in args[0]
    assert args[1] == 1
    assert args[2] == 2
    assert args[3] == "Ciao"


@pytest.mark.asyncio
async def test_find_messaggio_by_id():
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": 100, "titolo": "Test msg"}

    res = await messaggio_dao.find_messaggio_by_id(mock_conn, 100)
    assert res is not None
    assert res["id"] == 100
    assert res["titolo"] == "Test msg"
    mock_conn.fetchrow.assert_called_once_with(
        "SELECT * FROM messaggio WHERE id=$1", 100
    )


@pytest.mark.asyncio
async def test_find_messaggi_by_destinatario():
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = [{"id": 100, "id_destinatario": 5}]

    res = await messaggio_dao.find_messaggi_by_destinatario(mock_conn, 5)
    assert len(res) == 1
    assert res[0]["id_destinatario"] == 5
    mock_conn.fetch.assert_called_once_with(
        "SELECT * FROM messaggio WHERE id_destinatario=$1 ORDER BY id DESC", 5
    )


@pytest.mark.asyncio
async def test_find_messaggi_by_mittente():
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = [{"id": 101, "id_mittente": 3}]

    res = await messaggio_dao.find_messaggi_by_mittente(mock_conn, 3)
    assert len(res) == 1
    assert res[0]["id_mittente"] == 3
    mock_conn.fetch.assert_called_once_with(
        "SELECT * FROM messaggio WHERE id_mittente=$1 ORDER BY id DESC", 3
    )


@pytest.mark.asyncio
async def test_find_messaggi_by_tipo():
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = [{"id": 102, "tipo": "richiesta"}]

    res = await messaggio_dao.find_messaggi_by_tipo(mock_conn, "richiesta")
    assert len(res) == 1
    assert res[0]["tipo"] == "richiesta"
    mock_conn.fetch.assert_called_once_with(
        "SELECT * FROM messaggio WHERE tipo=$1 ORDER BY id DESC", "richiesta"
    )


@pytest.mark.asyncio
async def test_find_messaggi_by_tipo_and_riferito():
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = [{"id": 103, "tipo": "prestito", "id_riferito": 50}]

    res = await messaggio_dao.find_messaggi_by_tipo_and_riferito(
        mock_conn, "prestito", 50
    )
    assert len(res) == 1
    assert res[0]["id_riferito"] == 50
    mock_conn.fetch.assert_called_once_with(
        "SELECT * FROM messaggio WHERE tipo=$1 AND id_riferito=$2 ORDER BY id DESC",
        "prestito",
        50,
    )


@pytest.mark.asyncio
async def test_update_messaggio():
    mock_conn = AsyncMock()
    await messaggio_dao.update_messaggio(
        mock_conn, 100, {"titolo": "Nuovo titolo", "contenuto": "Nuovo testo"}
    )
    mock_conn.execute.assert_called_once()
    args = mock_conn.execute.call_args[0]
    assert "UPDATE messaggio SET" in args[0]
    assert args[1] == "Nuovo titolo"
    assert args[2] == "Nuovo testo"
    assert args[3] == 100


@pytest.mark.asyncio
async def test_delete_messaggio():
    mock_conn = AsyncMock()
    await messaggio_dao.delete_messaggio(mock_conn, 100)
    mock_conn.execute.assert_called_once_with("DELETE FROM messaggio WHERE id=$1", 100)
