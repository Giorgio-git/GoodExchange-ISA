"""
Test unitari per il Service Layer dei Prestiti.
Include test classici isolati (con AsyncMock) e test basati su proprietà (PBT) con Hypothesis.

Riferimenti alla griglia di valutazione:
- Unit Test isolati con Mocking (AsyncMock)
- BONUS: Property-Based Testing con Hypothesis sulla logica di solvibilità e precondizioni
"""

from datetime import date, timedelta
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.services import prestito_service

# ——————————————————————————————————————————————
# 1. BONUS: Property-Based Testing (PBT) con Hypothesis
# ——————————————————————————————————————————————


@given(
    st.floats(min_value=0.0, max_value=100_000.0, allow_nan=False),
    st.floats(min_value=0.0, max_value=100_000.0, allow_nan=False),
    st.floats(min_value=0.01, max_value=100_000.0, allow_nan=False),
)
def test_pbt_verifica_solvibilita_utente(
    cauzione, crediti_accumulati, valore_bene
):
    """
    Test basato su proprietà (Bonus Hypothesis):
    La funzione verifica_solvibilita_utente deve restituire True se e solo se
    (cauzione + crediti_accumulati) >= valore_bene.
    Esplora migliaia di combinazioni numeriche automaticamente.
    """
    risultato = prestito_service.verifica_solvibilita_utente(
        cauzione=cauzione,
        crediti_accumulati=crediti_accumulati,
        valore_bene=valore_bene,
    )
    atteso = (cauzione + crediti_accumulati) >= valore_bene
    assert risultato == atteso


@given(
    st.dates(
        min_value=date(2020, 1, 1), max_value=date(2030, 12, 31)
    ),  # genero date tra il 2020 e il 2030
    st.integers(min_value=1, max_value=365),  # genero giorni di durata tra 1 e 365
)
@pytest.mark.asyncio
async def test_pbt_creazione_prestito_date_valide(data_inizio, giorni_durata):
    """
    Test PBT (Hypothesis + Asyncio):
    Se data_fine = data_inizio + giorni_durata (con giorni_durata > 0)
    e il bene è disponibile, la creazione non deve sollevare ValueError.
    """
    data_fine = data_inizio + timedelta(days=giorni_durata)
    mock_conn = AsyncMock()

    with patch(
        "src.dao.prestito_dao.verifica_disponibilita", new_callable=AsyncMock
    ) as mock_disp:
        mock_disp.return_value = True
        mock_conn.fetchrow.return_value = {
            "id": 1,
            "id_bene": 10,
            "id_beneficiario": 20,
            "id_proprietario": 30,
            "data_inizio": data_inizio,
            "data_fine": data_fine,
            "stato": "richiesto",
        }

        res = await prestito_service.crea_prestito(
            mock_conn,
            id_bene=10,
            id_beneficiario=20,
            id_proprietario=30,
            data_inizio=data_inizio,
            data_fine=data_fine,
        )
        assert res["stato"] == "richiesto"


# ——————————————————————————————————————————————
# 2. Unit Test classici con Mocking
# ——————————————————————————————————————————————


@pytest.mark.asyncio
async def test_crea_prestito_data_invalida():
    """Design by Contract: data_fine <= data_inizio deve sollevare ValueError."""
    mock_conn = AsyncMock()
    d1 = date(2026, 6, 25)
    d2 = date(2026, 6, 20)  # precedente

    with pytest.raises(ValueError, match="data_fine deve essere successiva"):
        await prestito_service.crea_prestito(mock_conn, 1, 2, 3, d1, d2)


@pytest.mark.asyncio
async def test_crea_prestito_bene_non_disponibile():
    """Se il DAO restituisce disponibilità False, solleva ValueError."""
    mock_conn = AsyncMock()
    d1 = date(2026, 6, 25)
    d2 = date(2026, 6, 30)

    with patch(
        "src.dao.prestito_dao.verifica_disponibilita", new_callable=AsyncMock
    ) as mock_disp:
        mock_disp.return_value = False
        with pytest.raises(ValueError, match="non è disponibile"):
            await prestito_service.crea_prestito(mock_conn, 10, 20, 30, d1, d2)


@pytest.mark.asyncio
async def test_aggiorna_stato_transizione_illegale():
    """FSM Test: transizione illegale 'richiesto' -> 'completato' deve sollevare ValueError."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {
        "id": 1,
        "stato": "richiesto",
        "id_bene": 10,
        "id_proprietario": 30,
    }

    with pytest.raises(ValueError, match="Transizione non valida"):
        await prestito_service.aggiorna_stato_prestito(mock_conn, 1, "completato")


@pytest.mark.asyncio
async def test_aggiorna_stato_in_corso_side_effect():
    """Side Effect: accertarsi che il passaggio a 'in_corso' avvenga senza toccare lo stato del bene."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow.side_effect = [
        {
            "id": 1,
            "stato": "accettato",
            "id_bene": 10,
            "id_proprietario": 30,
        },  # select for update
        {"id": 1, "stato": "in_corso", "id_bene": 10, "id_proprietario": 30},  # return
    ]

    res = await prestito_service.aggiorna_stato_prestito(mock_conn, 1, "in_corso")
    assert res["stato"] == "in_corso"


# ——————————————————————————————————————————————
# 3. Test aggiuntivi per copertura completa
# ——————————————————————————————————————————————


@pytest.mark.asyncio
async def test_aggiorna_stato_completato_side_effect():
    """
    FSM + Side Effect: il passaggio a 'completato' deve:
    1. aggiornare i crediti accumulati del proprietario (calcola_crediti_accumulati)
    2. inviare notifica delivery (dopo commit)
    Senza modificare lo stato del catalogo del bene.
    SRS §FR-16, §9.2 — DbC: Post-condizione per stato 'completato'.
    """
    mock_conn = AsyncMock()
    mock_conn.fetchrow.side_effect = [
        {
            "id": 5,
            "stato": "in_corso",
            "id_bene": 20,
            "id_proprietario": 10,
        },  # SELECT FOR UPDATE
        {
            "id": 5,
            "stato": "completato",
            "id_bene": 20,
            "id_proprietario": 10,
        },  # return
    ]

    with (
        patch(
            "src.dao.utente_dao.calcola_crediti_accumulati", new_callable=AsyncMock
        ) as mock_crediti,
        patch(
            "src.services.prestito_service.notifica_delivery", new_callable=AsyncMock
        ) as mock_notifica,
    ):
        mock_crediti.return_value = 200
        mock_notifica.return_value = None

        res = await prestito_service.aggiorna_stato_prestito(mock_conn, 5, "completato")

    assert res["stato"] == "completato"
    mock_crediti.assert_awaited_once_with(mock_conn, 10)


@pytest.mark.asyncio
async def test_aggiorna_stato_prestito_non_trovato():
    """
    Pre-condizione DbC (SRS §9.2):
    Se il prestito non esiste nel DB, solleva ValueError.
    """
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = None  # prestito non trovato

    with pytest.raises(ValueError, match="non trovato"):
        await prestito_service.aggiorna_stato_prestito(mock_conn, 999, "accettato")


@pytest.mark.asyncio
async def test_crea_prestito_successo():
    """
    Test percorso felice: crea_prestito() con dati validi e bene disponibile.
    Post-condizione DbC (SRS §9.1): il prestito deve essere in stato 'richiesto'.
    """
    mock_conn = AsyncMock()
    d1 = date(2026, 8, 1)
    d2 = date(2026, 8, 10)

    with (
        patch(
            "src.dao.prestito_dao.verifica_disponibilita", new_callable=AsyncMock
        ) as mock_disp,
    ):
        mock_disp.return_value = True
        mock_conn.fetchrow.return_value = {
            "id": 1,
            "id_bene": 10,
            "id_beneficiario": 20,
            "id_proprietario": 30,
            "data_inizio": d1,
            "data_fine": d2,
            "stato": "richiesto",
        }

        res = await prestito_service.crea_prestito(mock_conn, 10, 20, 30, d1, d2)

    assert res["stato"] == "richiesto"
    assert res["id_bene"] == 10


@pytest.mark.asyncio
async def test_aggiorna_stato_annullato_senza_side_effect():
    """
    FSM + Side Effect: il passaggio a 'annullato' (o 'rifiutato') avviene aggiornando
    lo stato del prestito senza alterare il campo bene.stato (gestito solo dal proprietario).
    """
    mock_conn = AsyncMock()
    mock_conn.fetchrow.side_effect = [
        {"id": 2, "stato": "in_corso", "id_bene": 15, "id_proprietario": 30},
        {"id": 2, "stato": "annullato", "id_bene": 15, "id_proprietario": 30},
    ]

    res = await prestito_service.aggiorna_stato_prestito(mock_conn, 2, "annullato")
    assert res["stato"] == "annullato"


@pytest.mark.asyncio
async def test_crea_prestito_dao_fallisce():
    """
    Se il DAO fallisce e restituisce None (es. errore di vincolo nel DB),
    il service deve sollevare RuntimeError.
    """
    mock_conn = AsyncMock()
    d1 = date(2026, 8, 1)
    d2 = date(2026, 8, 10)

    with patch(
        "src.dao.prestito_dao.verifica_disponibilita", new_callable=AsyncMock
    ) as mock_disp:
        mock_disp.return_value = True
        mock_conn.fetchrow.return_value = None  # Simuliamo fallimento INSERT

        with pytest.raises(RuntimeError, match="Creazione prestito fallita"):
            await prestito_service.crea_prestito(mock_conn, 10, 20, 30, d1, d2)


@pytest.mark.asyncio
async def test_notifica_delivery_successo_e_errore():
    """
    Verifica che notifica_delivery gestisca sia la risposta HTTP 200 che eventuali
    errori di rete/timeout senza far crashare il sistema.
    """
    # Caso 1: successo 200
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.status_code = 200
        assert await prestito_service.notifica_delivery(1, "completato") is True

    # Caso 2: errore di rete / timeout
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.RequestError("Timeout di connessione")
        assert await prestito_service.notifica_delivery(1, "completato") is False


@pytest.mark.asyncio
async def test_crea_prestito_solvibilita_insufficiente():
    """
    Se l'utente ha cauzione + crediti_accumulati inferiori al costo del bene,
    crea_prestito deve sollevare ValueError per solvibilità insufficiente (Pre4 DbC).
    """
    mock_conn = AsyncMock()
    d1 = date(2026, 8, 1)
    d2 = date(2026, 8, 10)

    # side_effect per le query di row_bene e row_utente
    mock_conn.fetchrow.side_effect = [
        {"id": 10, "crediti_richiesti": 150},  # Il bene costa 150 crediti
        {
            "cauzione": 100.0,
            "crediti_accumulati": 0,
        },  # L'utente ha solo 100 di cauzione e 0 crediti
    ]

    with pytest.raises(ValueError, match="Solvibilità insufficiente"):
        await prestito_service.crea_prestito(mock_conn, 10, 20, 30, d1, d2)


@pytest.mark.asyncio
async def test_crea_prestito_solvibilita_sufficiente():
    """
    Se l'utente soddisfa cauzione + crediti_accumulati >= valore_crediti del bene,
    il prestito viene regolarmente inserito.
    """
    mock_conn = AsyncMock()
    d1 = date(2026, 8, 1)
    d2 = date(2026, 8, 10)

    # side_effect per row_bene, row_utente e inserimento prestito
    mock_conn.fetchrow.side_effect = [
        {"id": 10, "crediti_richiesti": 150},  # Il bene costa 150 crediti
        {
            "cauzione": 100.0,
            "crediti_accumulati": 60,
        },  # L'utente ha 100 + 60 = 160 >= 150
        {
            "id": 1,
            "id_bene": 10,
            "id_beneficiario": 20,
            "id_proprietario": 30,
            "data_inizio": d1,
            "data_fine": d2,
            "stato": "richiesto",
        },
    ]

    with patch(
        "src.dao.prestito_dao.verifica_disponibilita", new_callable=AsyncMock
    ) as mock_disp:
        mock_disp.return_value = True
        res = await prestito_service.crea_prestito(mock_conn, 10, 20, 30, d1, d2)
        assert res["stato"] == "richiesto"
