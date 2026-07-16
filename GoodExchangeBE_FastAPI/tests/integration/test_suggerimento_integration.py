"""Test di integrazione per suggerimento router (percorso felice)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_suggerimento_flusso_felice_integration(
    async_client: AsyncClient, utente_proprietario: dict
):
    """
    Verifica il ciclo di vita del percorso felice di un suggerimento:
    POST (creazione con stato 'richiesto') → GET (lista) → PUT (passaggio irreversibile a 'completato') → GET con filtro
    """
    id_mittente = utente_proprietario["id"]

    # 1. Creazione suggerimento (il DAO assegna di default stato = 'richiesto')
    payload = {
        "id_mittente": id_mittente,
    }
    res_create = await async_client.post("/api/suggerimenti", json=payload)
    assert res_create.status_code == 201
    data_create = res_create.json()
    suggerimento_id = data_create["id"]
    assert data_create["stato"] == "richiesto"

    # 2. GET lista suggerimenti (tutti)
    res_get_all = await async_client.get("/api/suggerimenti")
    assert res_get_all.status_code == 200
    ids = [s["id"] for s in res_get_all.json()]
    assert suggerimento_id in ids

    # 3. GET suggerimenti del mittente (per utente)
    res_get_user = await async_client.get(
        f"/api/suggerimenti/utente/{id_mittente}"
    )
    assert res_get_user.status_code == 200

    # 4. PUT — aggiornamento stato verso il secondo e ultimo stato consentito: 'completato'
    res_stato = await async_client.put(
        f"/api/suggerimenti/{suggerimento_id}/stato",
        json={"stato": "completato"},
    )
    assert res_stato.status_code == 200
    assert res_stato.json()["stato"] == "completato"

    # 5. GET con filtro per stato 'completato'
    res_filtro = await async_client.get(
        "/api/suggerimenti?stato=completato"
    )
    assert res_filtro.status_code == 200
    assert any(s["id"] == suggerimento_id for s in res_filtro.json())
