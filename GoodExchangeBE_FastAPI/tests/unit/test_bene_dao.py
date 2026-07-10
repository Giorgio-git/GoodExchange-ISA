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
    assert (
        "nome LIKE $1 OR descrizione LIKE $2" in call_args[0]
    )  # verifico la forma della query
    assert (
        call_args[1] == "%Harry Potter%"
    )  # verifico che l'argomento della query sia corretto
    assert call_args[3] == 10  # verifico che il limite sia corretto
