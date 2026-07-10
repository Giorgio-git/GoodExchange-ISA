"""
Test unitari per feedback_service.py

Struttura:
1. PBT con Hypothesis su calcola_reputazione_media_locale() (funzione pura)
   — SRS §FR-19, §9.4, INV-05: reputazione IN [1.0, 5.0]
2. Unit test con AsyncMock su crea_feedback_e_aggiorna_reputazione()

Riferimenti griglia di valutazione:
- Unit Test isolati con Mocking (AsyncMock)
- BONUS: Property-Based Testing con Hypothesis
"""

from unittest.mock import AsyncMock, patch

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.services import feedback_service

# ——————————————————————————————————————————————
# 1. PBT con Hypothesis — calcola_reputazione_media_locale (funzione pura)
# SRS §9.4, INV-05: reputazione IN [1.0, 5.0]
# ——————————————————————————————————————————————

# definiamo una strategia hypothesis per generare voti e liste di voti validi
voti_validi = st.integers(min_value=1, max_value=5)
lista_voti = st.lists(voti_validi, min_size=1, max_size=100) # una lista di voti validi che va da un voto singolo fino ad un massimo di 100 voti


@given(voti=lista_voti) # accettiamo le liste generate a caso
@settings(max_examples=500) # imposta il numero massimo di esempi che hypothesis deve generare
def test_pbt_reputazione_sempre_in_range(voti):
    """
    Invariante INV-05 (SRS §10):
    Per qualsiasi lista di voti validi, la reputazione media è sempre in [1.0, 5.0].
    """
    media = feedback_service.calcola_reputazione_media_locale(voti)
    assert 1.0 <= media <= 5.0


@given(voti=lista_voti)
@settings(max_examples=300)
def test_pbt_reputazione_e_media_aritmetica(voti):
    """
    Post-condizione §9.4:
    Il valore restituito è esattamente sum(voti) / len(voti).
    """
    media = feedback_service.calcola_reputazione_media_locale(voti)
    atteso = sum(voti) / len(voti)
    assert abs(media - atteso) < 1e-9 # verifico che il valore restituito sia uguale a quello calcolato manualmente in virgola mobile


def test_pbt_reputazione_lista_vuota_errore():
    """
    Pre-condizione violata: lista vuota deve sollevare ValueError.
    """
    with pytest.raises(ValueError, match="non può essere vuota"):
        feedback_service.calcola_reputazione_media_locale([])

# caso limite in cui abbiamo un solo voto
def test_reputazione_unico_voto_identita():
    """
    Edge case: un solo voto — la media deve essere il voto stesso.
    """
    for v in [1, 3, 5]:
        assert feedback_service.calcola_reputazione_media_locale([v]) == float(v)

# caso limite in cui tutti i voti sono uguali a 5
def test_reputazione_tutti_massimi():
    """
    Edge case: tutti voti massimi (5) — media deve essere 5.0.
    """
    assert feedback_service.calcola_reputazione_media_locale([5, 5, 5, 5]) == 5.0


# caso limite in cui tutti i voti sono uguali a 1
def test_reputazione_tutti_minimi():
    """
    Edge case: tutti voti minimi (1) — media deve essere 1.0.
    """
    assert feedback_service.calcola_reputazione_media_locale([1, 1, 1]) == 1.0


# ——————————————————————————————————————————————
# 2. Unit Test con AsyncMock — crea_feedback_e_aggiorna_reputazione()
# ——————————————————————————————————————————————


@pytest.mark.asyncio
async def test_crea_feedback_aggiorna_reputazione():
    """
    Test base: crea un feedback e verifica che la reputazione venga aggiornata.
    Design by Contract (SRS §9.4):
        Post: feedback creato in T_Feedback
        Post: utente[id_destinatario].reputazione = AVG(voti ricevuti)
    """
    mock_conn = AsyncMock()
    feedback_data = {
        "id_utente": 1,
        "id_destinatario": 2,
        "voto": 4,
        "data": None,
    }

    # sistituiamo tutte e tre le funzioni del DAO con le loro versioni mock
    with (
        patch("src.dao.feedback_dao.create_feedback", new_callable=AsyncMock) as mock_create,
        patch(
            "src.dao.feedback_dao.calcola_reputazione_media", new_callable=AsyncMock
        ) as mock_media,
        patch(
            "src.dao.feedback_dao.aggiorna_reputazione_utente", new_callable=AsyncMock
        ) as mock_aggiorna,
    ):
        mock_create.return_value = {"id": 10, **feedback_data}
        mock_media.return_value = 4.0
        mock_aggiorna.return_value = None

        result = await feedback_service.crea_feedback_e_aggiorna_reputazione(
            mock_conn, feedback_data
        )

    # Verifica post-condizioni
    assert result is not None
    assert result["id"] == 10
    mock_create.assert_awaited_once() # verifica che la mock function create sia stata chiamata una sola volta
    mock_media.assert_awaited_once_with(mock_conn, 2)  # destinatario corretto
    mock_aggiorna.assert_awaited_once_with(mock_conn, 2, 4.0) # verifica che la mock function aggiorna sia stata chiamata una sola volta con i parametri corretti


@pytest.mark.asyncio
async def test_crea_feedback_dao_fallisce():
    """
    Se il DAO create_feedback fallisce (restituisce None), il service restituisce None
    e non chiama calcola_reputazione_media.
    """
    mock_conn = AsyncMock()
    feedback_data = {"id_utente": 1, "id_destinatario": 2, "voto": 3}

    with (
        patch("src.dao.feedback_dao.create_feedback", new_callable=AsyncMock) as mock_create,
        patch(
            "src.dao.feedback_dao.calcola_reputazione_media", new_callable=AsyncMock
        ) as mock_media,
    ):
        mock_create.return_value = None

        result = await feedback_service.crea_feedback_e_aggiorna_reputazione(
            mock_conn, feedback_data
        )

    assert result is None
    mock_media.assert_not_awaited()  # non deve calcolare la media se il feedback non è creato
