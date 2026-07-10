import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_recensione_flusso_completo_integration(
    async_client: AsyncClient,
    utente_beneficiario: dict,
    bene_test: dict,
):
    """
    Verifica Creazione, Lettura per ID e con filtri, Aggiornamento ed Eliminazione di una recensione.
    """
    id_beneficiario = utente_beneficiario["id"]
    id_bene = bene_test["id"]

    payload_create = {
        "id_bene": id_bene,
        "id_beneficiario": id_beneficiario,
        "voto": 4,
    }

    # 1. Creazione (POST /api/recensioni)
    res_create = await async_client.post("/api/recensioni", json=payload_create)
    assert res_create.status_code == 201
    rec_id = res_create.json()["id"]

    # 2. Lettura per ID (GET /api/recensioni/:id)
    res_get = await async_client.get(f"/api/recensioni/{rec_id}")
    assert res_get.status_code == 200
    assert res_get.json()["voto"] == 4

    # 3. Lettura con filtro per bene (GET /api/recensioni?id_bene=...)
    res_filter = await async_client.get(f"/api/recensioni?id_bene={id_bene}")
    assert res_filter.status_code == 200
    assert any(r["id"] == rec_id for r in res_filter.json())

    # 4. Aggiornamento (PUT /api/recensioni/:id)
    res_update = await async_client.put(f"/api/recensioni/{rec_id}", json={"voto": 5})
    assert res_update.status_code == 200

    res_get_upd = await async_client.get(f"/api/recensioni/{rec_id}")
    assert res_get_upd.json()["voto"] == 5

    # 5. Eliminazione (DELETE /api/recensioni/:id)
    res_del = await async_client.delete(f"/api/recensioni/{rec_id}")
    assert res_del.status_code == 200

    # 6. Verifica eliminazione (GET /api/recensioni/:id -> 404)
    res_404 = await async_client.get(f"/api/recensioni/{rec_id}")
    assert res_404.status_code == 404
