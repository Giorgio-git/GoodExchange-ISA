"""
Test unitari per utente_service.py

Struttura:
1. PBT con Hypothesis su verifica_solvibilita_utente() (funzione pura)
   — SRS §9.3, BK-01
2. Unit test classici con AsyncMock su registra_utente()

Riferimenti griglia di valutazione:
- Unit Test isolati con Mocking (AsyncMock)
- BONUS: Property-Based Testing con Hypothesis
"""

from unittest.mock import AsyncMock, patch

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.services import utente_service

# ——————————————————————————————————————————————
# 1. PBT con Hypothesis — verifica_solvibilita_utente (funzione pura)
# SRS §9.3, BK-01: cauzione + crediti_accumulati >= valore_bene
# ——————————————————————————————————————————————


@given(
    cauzione=st.floats(min_value=0.0, max_value=100_000.0, allow_nan=False),
    crediti_accumulati=st.floats(min_value=0.0, max_value=100_000.0, allow_nan=False),
    valore_bene=st.floats(min_value=0.01, max_value=100_000.0, allow_nan=False),
)
@settings(max_examples=500)
def test_pbt_verifica_solvibilita_correttezza(
    cauzione, crediti_accumulati, valore_bene
):
    """
    PBT — Proprietà matematica (SRS §9.3):
    Per qualsiasi combinazione valida di input, la funzione deve restituire
    esattamente (cauzione + crediti_accumulati) >= valore_bene.
    """
    atteso = (cauzione + crediti_accumulati) >= valore_bene
    assert (
        utente_service.verifica_solvibilita_utente(
            cauzione, crediti_accumulati, valore_bene
        )
        == atteso
    )


@given(
    cauzione=st.floats(min_value=0.0, max_value=1000.0, allow_nan=False),
    crediti_accumulati=st.floats(min_value=0.0, max_value=1000.0, allow_nan=False),
    valore_bene=st.floats(min_value=0.01, max_value=500.0, allow_nan=False),
)
def test_pbt_solvibilita_monotona(cauzione, crediti_accumulati, valore_bene):
    """
    PBT — Proprietà di monotonicità:
    Se solvibile con crediti X, lo è anche con crediti X+1.
    """
    if utente_service.verifica_solvibilita_utente(
        cauzione, crediti_accumulati, valore_bene
    ):
        assert utente_service.verifica_solvibilita_utente(
            cauzione, crediti_accumulati + 1.0, valore_bene
        )


def test_pbt_solvibilita_edge_case_uguaglianza():
    """
    Edge case DbC: cauzione + crediti == valore_bene deve essere True (BK-01 usa >=).
    """
    assert utente_service.verifica_solvibilita_utente(50.0, 50.0, 100.0) is True


def test_pbt_solvibilita_edge_case_insufficiente():
    """
    Edge case DbC: cauzione + crediti < valore_bene deve essere False.
    """
    assert utente_service.verifica_solvibilita_utente(49.0, 50.0, 100.0) is False


def test_solvibilita_precondizione_cauzione_negativa():
    """
    Pre-condizione violata: cauzione < 0 deve sollevare ValueError.
    """
    with pytest.raises(ValueError, match="cauzione deve essere >= 0"):
        utente_service.verifica_solvibilita_utente(-1.0, 50.0, 100.0)


def test_solvibilita_precondizione_valore_bene_zero():
    """
    Pre-condizione violata: valore_bene <= 0 deve sollevare ValueError.
    """
    with pytest.raises(ValueError, match="valore_bene deve essere > 0"):
        utente_service.verifica_solvibilita_utente(100.0, 50.0, 0.0)


def test_solvibilita_precondizione_crediti_negativi():
    """
    Pre-condizione DbC violata: crediti_accumulati < 0 deve sollevare ValueError.
    """
    with pytest.raises(ValueError, match="crediti_accumulati deve essere >= 0"):
        utente_service.verifica_solvibilita_utente(100.0, -10.0, 50.0)


# ——————————————————————————————————————————————
# 2. Unit Test con AsyncMock — registra_utente()
# ——————————————————————————————————————————————


@pytest.mark.asyncio
async def test_registra_utente_successo():
    """
    Test base: registra_utente() deve creare l'utente e restituirlo senza password.
    """
    mock_conn = AsyncMock()
    utente_data = {
        "username": "testuser",
        "password": "secret123",
        "nome": "Mario",
        "cognome": "Rossi",
        "codice_fiscale": "RSSMRA80A01H501Z",
        "regione": "Emilia-Romagna",
        "provincia": "FE",
        "citta": "Ferrara",
        "via": "Via Roma",
        "civico": "1",
    }

    with patch(
        "src.dao.utente_dao.create_utente", new_callable=AsyncMock
    ) as mock_create:
        mock_create.return_value = {
            **utente_data,
            "id": 42,
            "id_utente": 42,
            "ruolo": "utente",
            "stato": "attivo",
            "crediti_valore_beni": 0,
            "crediti_accumulati": 0,
            "cauzione": 0.0,
        }
        result = await utente_service.registra_utente(mock_conn, dict(utente_data))

    # Post-condizione: la password NON deve essere nella risposta (SRS §NFR-05)
    assert "password" not in result
    assert result["id"] == 42
    assert result["username"] == "testuser"


@pytest.mark.asyncio
async def test_registra_utente_ruolo_predefinito():
    """
    Business Rule: il ruolo predefinito deve essere 'utente', non 'admin'.
    """
    mock_conn = AsyncMock()
    utente_data = {"username": "u1", "password": "pw"}

    with patch(
        "src.dao.utente_dao.create_utente", new_callable=AsyncMock
    ) as mock_create:
        mock_create.return_value = {**utente_data, "id": 1, "ruolo": "utente"}
        await utente_service.registra_utente(mock_conn, dict(utente_data))

        # Verifica che il ruolo sia stato impostato a 'utente' prima della chiamata DAO
        call_kwargs = mock_create.call_args[0][1]
        assert call_kwargs.get("ruolo") == "utente"


@pytest.mark.asyncio
async def test_registra_utente_dao_fallisce():
    """
    Se il DAO restituisce None (es. username duplicato), il service restituisce None.
    """
    mock_conn = AsyncMock()

    with patch(
        "src.dao.utente_dao.create_utente", new_callable=AsyncMock
    ) as mock_create:
        mock_create.return_value = None
        result = await utente_service.registra_utente(mock_conn, {"username": "dup"})

    assert result is None
