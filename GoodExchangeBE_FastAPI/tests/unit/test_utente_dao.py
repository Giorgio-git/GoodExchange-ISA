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


@pytest.mark.asyncio
async def test_find_utente_by_id():
    """Verifica che find_utente_by_id restituisca il dict utente dato l'ID."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow.side_effect = [
        {"id": 5, "username": "mario", "ruolo": "utente"},  # SELECT utente
        {"media": None},  # SELECT reputazione
    ]
    res = await utente_dao.find_utente_by_id(mock_conn, 5)
    assert res is not None
    assert res["username"] == "mario"


@pytest.mark.asyncio
async def test_find_utente_by_id_not_found():
    """Verifica che find_utente_by_id restituisca None se l'utente non esiste."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = None
    res = await utente_dao.find_utente_by_id(mock_conn, 9999)
    assert res is None


@pytest.mark.asyncio
async def test_update_utente_cauzione():
    """Verifica che update_utente_cauzione esegua UPDATE correttamente."""
    mock_conn = AsyncMock()
    mock_conn.execute.return_value = "UPDATE 1"
    success = await utente_dao.update_utente_cauzione(mock_conn, 1, 150.0)
    assert success is True
    mock_conn.execute.assert_called_once_with(
        "UPDATE utente SET cauzione=$1 WHERE id=$2", 150.0, 1
    )


@pytest.mark.asyncio
async def test_create_utente():
    """Verifica che create_utente esegua INSERT e restituisca il dict con l'id generato."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {"id": 99}
    utente_data = {
        "username": "nuovo_user",
        "password": "hash",
        "nome": "Nuovo",
        "cognome": "Utente",
        "codice_fiscale": "ABCDEF80A01H501Z",
        "regione": "Lombardia",
        "provincia": "MI",
        "citta": "Milano",
        "via": "Via Verdi",
        "civico": "10",
        "ruolo": "utente",
    }
    res = await utente_dao.create_utente(mock_conn, utente_data)
    assert res is not None
    assert res["id"] == 99
    mock_conn.fetchrow.assert_called_once()
    call_args = mock_conn.fetchrow.call_args[0]
    assert "INSERT INTO utente" in call_args[0]


@pytest.mark.asyncio
async def test_update_utente():
    """Verifica che update_utente costruisca e i parametri e la query UPDATE."""
    mock_conn = AsyncMock()
    mock_conn.execute.return_value = "UPDATE 1"
    aggiornamento = {"nome": "NuovoNome", "citta": "Roma"}
    res = await utente_dao.update_utente(mock_conn, 3, aggiornamento)
    assert res == []
    call_args = mock_conn.execute.call_args[0]
    assert "UPDATE utente SET" in call_args[0]
    assert "WHERE id = $3" in call_args[0]


@pytest.mark.asyncio
async def test_update_utente_vuoto():
    """Verifica che update_utente con dizionario vuoto o valori None non esegua query."""
    mock_conn = AsyncMock()
    res = await utente_dao.update_utente(mock_conn, 3, {"nome": ""})
    assert res == []
    mock_conn.execute.assert_not_called()


@pytest.mark.asyncio
async def test_update_utente_stato():
    """Verifica che update_utente_stato esegua UPDATE e restituisca True."""
    mock_conn = AsyncMock()
    mock_conn.execute.return_value = "UPDATE 1"
    success = await utente_dao.update_utente_stato(mock_conn, 4, "disattivo")
    assert success is True
    mock_conn.execute.assert_called_once_with(
        "UPDATE utente SET stato=$1 WHERE id=$2", "disattivo", 4
    )


@pytest.mark.asyncio
async def test_calcola_crediti_valore_beni():
    """Verifica che calcola_crediti_valore_beni recuperi il totale e aggiorni l'utente."""
    mock_conn = AsyncMock()
    mock_conn.fetchval.return_value = 150
    mock_conn.execute.return_value = "UPDATE 1"
    totale = await utente_dao.calcola_crediti_valore_beni(mock_conn, 5)
    assert totale == 150
    mock_conn.fetchval.assert_called_once()
    mock_conn.execute.assert_called_once_with(
        "UPDATE utente SET crediti_valore_beni = $1 WHERE id = $2", 150, 5
    )


@pytest.mark.asyncio
async def test_calcola_crediti_accumulati():
    """Verifica che calcola_crediti_accumulati recuperi il totale dei prestiti completati e aggiorni l'utente."""
    mock_conn = AsyncMock()
    mock_conn.fetchval.return_value = 200
    mock_conn.execute.return_value = "UPDATE 1"
    totale = await utente_dao.calcola_crediti_accumulati(mock_conn, 5)
    assert totale == 200
    mock_conn.fetchval.assert_called_once()
    mock_conn.execute.assert_called_once_with(
        "UPDATE utente SET crediti_accumulati = $1 WHERE id = $2", 200, 5
    )
