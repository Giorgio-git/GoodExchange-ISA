"""
Test unitari per bene_service.py

Struttura:
1. Unit test con AsyncMock su crea_bene_con_crediti()
   — verifica che il service chiami create_bene_raw + calcola_crediti_valore_beni
2. Unit test con AsyncMock su elimina_bene_con_crediti()
   — verifica che il service chiami delete_bene + calcola_crediti_valore_beni
"""

from unittest.mock import AsyncMock, patch

import pytest

from src.services import bene_service

# Test delle regole di business associate ai beni

# ——————————————————————————————————————————————
# 1. Test su crea_bene_con_crediti()
# ——————————————————————————————————————————————

# verifica che quando un bene viene creato venga aggiornato il contatore dei crediti dell'utente che lo ha aggiunto


@pytest.mark.asyncio
async def test_crea_bene_aggiorna_crediti():
    """
    Post-condizione DbC:
    Dopo la creazione del bene, calcola_crediti_valore_beni deve essere
    chiamato esattamente una volta per il proprietario.
    """
    mock_conn = AsyncMock()
    bene_data = {
        "id_proprietario": 5,
        "id_categoria": 2,
        "nome": "Trapano Bosch",
        "descrizione": "Ottimo stato",
        "peso": 1.5,
        "stato": True,
    }

    with (
        patch(
            "src.dao.bene_dao.create_bene_raw", new_callable=AsyncMock
        ) as mock_create,  # all'interno di questo test la funzione create_bene_raw viene sostituita da una mock function chiamata mock_create e lo stesso vale per calcola_crediti_valore_beni con mock_crediti
        patch(
            "src.dao.utente_dao.calcola_crediti_valore_beni", new_callable=AsyncMock
        ) as mock_crediti,  # la funzione calcola_crediti_valore_beni viene sostituita da una mock function chiamata mock_crediti
    ):
        mock_create.return_value = {
            **bene_data,
            "id": 42,
        }  # simula il risultato della query che crea il bene
        mock_crediti.return_value = (
            100  # simula il risultato della query che calcola i crediti
        )

        result = await bene_service.crea_bene_con_crediti(
            mock_conn, bene_data
        )  # chiamata alla funzione crea_bene_con_crediti del service layer passando il mock e il dizionario dei dati del bene

    # Post-condizioni
    assert (
        result is not None
    )  # verifichiamo che il servizio abbia restituito un risultato
    assert (
        result["id"] == 42
    )  # verifichiamo che il servizio abbia restituito il bene con l'id corretto
    mock_create.assert_awaited_once_with(
        mock_conn, bene_data
    )  # verifichiamo che il dao sia stato chiamato una sola volta con i dati corretti
    mock_crediti.assert_awaited_once_with(
        mock_conn, 5
    )  # verifichiamo che il calcolo dei crediti sia stato chiamato una sola volta con l'id corretto


@pytest.mark.asyncio
async def test_crea_bene_dao_fallisce_nessun_credito_update():
    """
    Se il DAO create_bene_raw fallisce (restituisce None), il service deve
    restituire None senza chiamare calcola_crediti_valore_beni.
    Principio: non si aggiornano crediti se il bene non è stato creato.
    """
    mock_conn = AsyncMock()
    bene_data = {"id_proprietario": 5, "id_categoria": 2, "nome": "Test"}

    with (
        patch(
            "src.dao.bene_dao.create_bene_raw", new_callable=AsyncMock
        ) as mock_create,
        patch(
            "src.dao.utente_dao.calcola_crediti_valore_beni", new_callable=AsyncMock
        ) as mock_crediti,
    ):
        mock_create.return_value = None

        result = await bene_service.crea_bene_con_crediti(mock_conn, bene_data)

    assert (
        result is None
    )  # verifichiamo che il servizio abbia restituito un risultato nullo
    mock_crediti.assert_not_awaited()  # verifichiamo che la mock function calcola_crediti sia stata chiamata zero volte


# verifichiamo che il dao venga chiamato con i dati corretti senza verificare errori sul calcolo dei crediti tenendo separate le responsabilità dei test
@pytest.mark.asyncio
async def test_crea_bene_chiama_create_con_dati_corretti():
    """
    Verifica che il DAO venga chiamato con esattamente i dati forniti dal router.
    """
    mock_conn = AsyncMock()
    bene_data = {"id_proprietario": 7, "id_categoria": 3, "nome": "Scala"}

    with (
        patch(
            "src.dao.bene_dao.create_bene_raw", new_callable=AsyncMock
        ) as mock_create,
        patch("src.dao.utente_dao.calcola_crediti_valore_beni", new_callable=AsyncMock),
    ):
        mock_create.return_value = {**bene_data, "id": 99}
        await bene_service.crea_bene_con_crediti(mock_conn, bene_data)

    # Il DAO deve ricevere esattamente il dict dei dati (nessuna modifica)
    mock_create.assert_awaited_once_with(mock_conn, bene_data)


# ——————————————————————————————————————————————
# 2. Test su elimina_bene_con_crediti()
# ——————————————————————————————————————————————


@pytest.mark.asyncio
async def test_elimina_bene_aggiorna_crediti():
    """
    Post-condizione DbC:
    Dopo l'eliminazione del bene, i crediti_valore_beni del proprietario
    devono essere ricalcolati (il bene è già rimosso dal DB).
    """
    mock_conn = AsyncMock()

    with (
        patch("src.dao.bene_dao.delete_bene", new_callable=AsyncMock) as mock_delete,
        patch(
            "src.dao.utente_dao.calcola_crediti_valore_beni", new_callable=AsyncMock
        ) as mock_crediti,
    ):
        mock_delete.return_value = True
        mock_crediti.return_value = 50

        result = await bene_service.elimina_bene_con_crediti(
            mock_conn, id_bene=10, id_proprietario=5
        )

    assert result is True
    mock_delete.assert_awaited_once_with(mock_conn, 10)
    mock_crediti.assert_awaited_once_with(mock_conn, 5)


@pytest.mark.asyncio
async def test_elimina_bene_non_trovato():
    """
    Se il DAO non trova il bene (restituisce False), il service deve
    restituire False senza chiamare calcola_crediti_valore_beni.
    """
    mock_conn = AsyncMock()

    with (
        patch("src.dao.bene_dao.delete_bene", new_callable=AsyncMock) as mock_delete,
        patch(
            "src.dao.utente_dao.calcola_crediti_valore_beni", new_callable=AsyncMock
        ) as mock_crediti,
    ):
        mock_delete.return_value = False

        result = await bene_service.elimina_bene_con_crediti(
            mock_conn, id_bene=99, id_proprietario=5
        )

    assert result is False
    mock_crediti.assert_not_awaited()  # la funzione che aggiorna i crediti non deve essere chiamata neanche una volta


@pytest.mark.asyncio
async def test_blocca_bene_aggiorna_crediti():
    """Testa che il blocco di un bene ricalcoli i crediti del proprietario."""
    mock_conn = AsyncMock()
    with (
        patch("src.dao.bene_dao.find_bene_by_id", new_callable=AsyncMock) as mock_find,
        patch("src.dao.bene_dao.block_bene", new_callable=AsyncMock) as mock_block,
        patch(
            "src.dao.utente_dao.calcola_crediti_valore_beni", new_callable=AsyncMock
        ) as mock_crediti,
    ):
        mock_find.return_value = {"id": 10, "id_proprietario": 5}
        mock_block.return_value = True

        result = await bene_service.blocca_bene_con_crediti(mock_conn, id_bene=10)

    assert result is True
    mock_block.assert_awaited_once_with(mock_conn, 10)
    mock_crediti.assert_awaited_once_with(mock_conn, 5)


@pytest.mark.asyncio
async def test_sblocca_bene_aggiorna_crediti():
    """Testa che lo sblocco di un bene ricalcoli i crediti del proprietario."""
    mock_conn = AsyncMock()
    with (
        patch("src.dao.bene_dao.find_bene_by_id", new_callable=AsyncMock) as mock_find,
        patch("src.dao.bene_dao.unblock_bene", new_callable=AsyncMock) as mock_unblock,
        patch(
            "src.dao.utente_dao.calcola_crediti_valore_beni", new_callable=AsyncMock
        ) as mock_crediti,
    ):
        mock_find.return_value = {"id": 10, "id_proprietario": 5}
        mock_unblock.return_value = True

        result = await bene_service.sblocca_bene_con_crediti(mock_conn, id_bene=10)

    assert result is True
    mock_unblock.assert_awaited_once_with(mock_conn, 10)
    mock_crediti.assert_awaited_once_with(mock_conn, 5)


@pytest.mark.asyncio
async def test_aggiorna_bene_aggiorna_crediti_quando_stato_o_categoria_cambia():
    """Testa che l'aggiornamento con cambio stato o categoria ricalcoli i crediti."""
    mock_conn = AsyncMock()
    with (
        patch("src.dao.bene_dao.find_bene_by_id", new_callable=AsyncMock) as mock_find,
        patch("src.dao.bene_dao.update_bene", new_callable=AsyncMock) as mock_update,
        patch(
            "src.dao.utente_dao.calcola_crediti_valore_beni", new_callable=AsyncMock
        ) as mock_crediti,
    ):
        mock_find.return_value = {"id": 10, "id_proprietario": 5}
        mock_update.return_value = True

        result = await bene_service.aggiorna_bene_con_crediti(
            mock_conn, id_bene=10, aggiornamenti={"stato": False}
        )

    assert result is True
    mock_update.assert_awaited_once_with(mock_conn, 10, {"stato": False})
    mock_crediti.assert_awaited_once_with(mock_conn, 5)
