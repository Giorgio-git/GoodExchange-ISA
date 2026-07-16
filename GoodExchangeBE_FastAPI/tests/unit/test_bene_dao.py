"""Test unitari isolati per Bene DAO."""

from unittest.mock import AsyncMock

import pytest

from src.dao import bene_dao


@pytest.mark.asyncio
async def test_find_beni_by_proprietari():
    mock_conn = AsyncMock()  # creo un mock asincrono per la connessione al database
    mock_conn.fetch.return_value = [
        {"id": 10, "nome": "Libro", "id_proprietario": 1}
    ]  # uso uno stub per simulare il risultato della query simulando la risposta di una chiamata al db

    res = await bene_dao.find_beni_by_proprietari(
        mock_conn, [1, 2, 3]
    )  # passo il mock e la lista di proprietari
    assert len(res) == 1  # verifico che la lista non sia vuota
    assert res[0]["nome"] == "Libro"  # verifico che il nome sia corretto
    call_args = mock_conn.fetch.call_args[
        0
    ]  # prendo gli argomenti passati al mock sotto forma di tupla (la query, gli argomenti della query)
    assert (
        "ANY($1)" in call_args[0]
    )  # verifico che la query contenga la keyword ANY($1)
    assert call_args[1] == [
        1,
        2,
        3,
    ]  # verifico che gli argomenti della query siano corretti


@pytest.mark.asyncio
async def test_find_beni_ricerca_testuale():
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = []  # la query restituirà una lista vuota (vogliamo vedere quale query costruisce il dao)

    await bene_dao.find_beni(
        mock_conn, {"search": "Harry Potter", "limit": 10}
    )  # passo il mock e un dizionario con la ricerca e il limite di risultati
    call_args = mock_conn.fetch.call_args[0]
    assert "nome ILIKE $1" in call_args[0]  # verifico la forma della query
    assert (
        call_args[1] == "%Harry Potter%"
    )  # verifico che l'argomento della query sia corretto
    assert call_args[2] == 10  # verifico che il limite sia corretto


@pytest.mark.asyncio
async def test_create_bene_raw():
    """Verifica che create_bene_raw esegua INSERT e restituisca il dict con l'id generato."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": 42}
    bene_data = {
        "id_proprietario": 1,
        "id_categoria": 2,
        "nome": "Trapano",
        "descrizione": "Ottimo stato",
        "peso": 1.5,
        "stato": True,
    }
    res = await bene_dao.create_bene_raw(mock_conn, bene_data)
    assert res is not None
    assert res["id"] == 42
    assert res["nome"] == "Trapano"
    mock_conn.fetchrow.assert_called_once()
    call_args = mock_conn.fetchrow.call_args[0]
    assert "INSERT INTO bene" in call_args[0]


@pytest.mark.asyncio
async def test_find_bene_by_id():
    """Verifica che find_bene_by_id restituisca il dict del bene dato l'ID."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": 10, "nome": "Scala", "id_proprietario": 3}
    res = await bene_dao.find_bene_by_id(mock_conn, 10)
    assert res is not None
    assert res["id"] == 10
    mock_conn.fetchrow.assert_called_once()


@pytest.mark.asyncio
async def test_find_bene_by_id_not_found():
    """Verifica che find_bene_by_id restituisca None se il bene non esiste."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = None
    res = await bene_dao.find_bene_by_id(mock_conn, 9999)
    assert res is None


@pytest.mark.asyncio
async def test_update_bene():
    """Verifica che update_bene costruisca la query UPDATE dinamica correttamente."""
    mock_conn = AsyncMock()
    mock_conn.execute.return_value = "UPDATE 1"
    aggiornamenti = {"nome": "Nuovo Nome", "peso": 2.0}
    success = await bene_dao.update_bene(mock_conn, 5, aggiornamenti)
    assert success is True
    call_args = mock_conn.execute.call_args[0]
    assert "UPDATE bene SET" in call_args[0]
    assert "WHERE" in call_args[0]


@pytest.mark.asyncio
async def test_block_bene():
    """Verifica che block_bene imposti stato=False nel DB."""
    mock_conn = AsyncMock()
    mock_conn.execute.return_value = "UPDATE 1"
    success = await bene_dao.block_bene(mock_conn, 7)
    assert success is True
    mock_conn.execute.assert_called_once_with(
        "UPDATE bene SET stato=$1 WHERE id=$2", False, 7
    )


@pytest.mark.asyncio
async def test_unblock_bene():
    """Verifica che unblock_bene imposti stato=True nel DB."""
    mock_conn = AsyncMock()
    mock_conn.execute.return_value = "UPDATE 1"
    success = await bene_dao.unblock_bene(mock_conn, 7)
    assert success is True
    mock_conn.execute.assert_called_once_with(
        "UPDATE bene SET stato=$1 WHERE id=$2", True, 7
    )


@pytest.mark.asyncio
async def test_delete_bene():
    """Verifica che delete_bene esegua la DELETE corretta."""
    mock_conn = AsyncMock()
    mock_conn.execute.return_value = "DELETE 1"
    success = await bene_dao.delete_bene(mock_conn, 10)
    assert success is True
    mock_conn.execute.assert_called_once_with("DELETE FROM bene WHERE id = $1", 10)


@pytest.mark.asyncio
async def test_update_bene_immagine():
    """Verifica che update_bene_immagine esegua UPDATE con bytes corretti."""
    mock_conn = AsyncMock()
    fake_bytes = b"fakepngcontent"
    await bene_dao.update_bene_immagine(mock_conn, 3, fake_bytes)
    mock_conn.execute.assert_called_once_with(
        "UPDATE bene SET immagine = $1 WHERE id = $2", fake_bytes, 3
    )


@pytest.mark.asyncio
async def test_get_bene_immagine():
    """Verifica che get_bene_immagine restituisca i bytes dell'immagine."""
    mock_conn = AsyncMock()
    fake_bytes = b"fakepngcontent"
    mock_conn.fetchrow.return_value = {"immagine": fake_bytes}
    res = await bene_dao.get_bene_immagine(mock_conn, 3)
    assert res == fake_bytes


@pytest.mark.asyncio
async def test_get_bene_immagine_none():
    """Verifica che get_bene_immagine restituisca None se non c'è immagine."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"immagine": None}
    res = await bene_dao.get_bene_immagine(mock_conn, 3)
    assert res is None


@pytest.mark.asyncio
async def test_delete_bene_immagine():
    """Verifica che delete_bene_immagine esegua UPDATE immagine=NULL."""
    mock_conn = AsyncMock()
    await bene_dao.delete_bene_immagine(mock_conn, 3)
    mock_conn.execute.assert_called_once_with(
        "UPDATE bene SET immagine = NULL WHERE id = $1", 3
    )
