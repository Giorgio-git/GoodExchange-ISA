import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_categoria_crud_integration(async_client: AsyncClient):
    """
    Verifica il flusso completo di Creazione, Lettura, Aggiornamento ed Eliminazione (CRUD)
    per l'entità Categoria sul database PostgreSQL di test.
    """
    nome_cat = f"Cat_int_{uuid.uuid4().hex[:6]}"
    payload_create = {
        "nome": nome_cat,
        "crediti": 10,
        "descrizione": "Categoria per integration testing",
    }

    # 1. Creazione (POST)
    res_create = await async_client.post("/api/categorie", json=payload_create)
    assert res_create.status_code == 201
    cat_data = res_create.json()
    assert cat_data["nome"] == nome_cat
    assert cat_data["crediti"] == 10
    cat_id = cat_data["id"]

    # 2. Lettura per ID (GET /api/categorie/:id)
    res_get = await async_client.get(f"/api/categorie/{cat_id}")
    assert res_get.status_code == 200
    assert res_get.json()["descrizione"] == "Categoria per integration testing"

    # 3. Lista e verifica ordinamento (GET /api/categorie)
    res_list = await async_client.get("/api/categorie")
    assert res_list.status_code == 200
    elenco = res_list.json()
    assert any(c["id"] == cat_id for c in elenco)

    # 4. Aggiornamento (PUT /api/categorie/:id)
    res_update = await async_client.put(
        f"/api/categorie/{cat_id}",
        json={"crediti": 25, "descrizione": "Descrizione aggiornata"},
    )
    assert res_update.status_code == 200

    res_get_updated = await async_client.get(f"/api/categorie/{cat_id}")
    assert res_get_updated.json()["crediti"] == 25
    assert res_get_updated.json()["descrizione"] == "Descrizione aggiornata"

    # 5. Eliminazione (DELETE /api/categorie/:id)
    res_del = await async_client.delete(f"/api/categorie/{cat_id}")
    assert res_del.status_code == 200

    # 6. Verifica eliminazione avvenuta (404 Not Found)
    res_get_after_del = await async_client.get(f"/api/categorie/{cat_id}")
    assert res_get_after_del.status_code == 404
