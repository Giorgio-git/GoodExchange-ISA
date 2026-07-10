import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_segnalazione_flusso_completo_integration(
    async_client: AsyncClient,
    utente_proprietario: dict,
    utente_beneficiario: dict,
):
    """Verifica apertura di una segnalazione, lettura, filtro per stato e risoluzione da parte dell'amministrazione."""
    id_segnalante = utente_beneficiario["id"]
    id_segnalato = utente_proprietario["id"]

    payload_create = {
        "id_segnalante": id_segnalante,
        "id_segnalato": id_segnalato,
        "stato": "aperta",
    }

    # 1. Creazione (POST /api/segnalazioni)
    res_create = await async_client.post("/api/segnalazioni", json=payload_create)
    assert res_create.status_code == 201
    seg_id = res_create.json()["id"]

    # 2. Lettura per ID (GET /api/segnalazioni/:id)
    res_get = await async_client.get(f"/api/segnalazioni/{seg_id}")
    assert res_get.status_code == 200
    assert res_get.json()["stato"] == "aperta"

    # 3. Filtro per stato (GET /api/segnalazioni?stato=aperta)
    res_filter = await async_client.get("/api/segnalazioni?stato=aperta")
    assert res_filter.status_code == 200
    assert any(s["id"] == seg_id for s in res_filter.json())

    # 4. Modifica stato in "risolta" (PUT /api/segnalazioni/:id/stato)
    res_update = await async_client.put(
        f"/api/segnalazioni/{seg_id}/stato",
        json={"stato": "risolta"},
    )
    assert res_update.status_code == 200

    # 5. Verifica che lo stato sia stato effettivamente modificato nel DB
    res_get_upd = await async_client.get(f"/api/segnalazioni/{seg_id}")
    assert res_get_upd.json()["stato"] == "risolta"
