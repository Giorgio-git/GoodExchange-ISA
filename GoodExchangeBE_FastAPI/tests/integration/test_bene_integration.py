import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_bene_flusso_completo_e_crediti_integration(
    async_client: AsyncClient,
    utente_proprietario: dict,
    categoria_test: dict,
):
    """
    Verifica la creazione, lettura, ricerca e cancellazione di un bene,
    nonché l'aggiornamento automatico dei crediti del proprietario (logica Three-Tier in bene_service).
    """
    nome_bene = f"Libro_int_{uuid.uuid4().hex[:6]}"
    proprietario_id = utente_proprietario["id"]
    cat_id = categoria_test["id"]

    # 0. Verifica crediti iniziali proprietario
    res_cred_pre = await async_client.get(f"/api/utenti/{proprietario_id}/crediti")
    assert res_cred_pre.status_code == 200
    crediti_iniziali = res_cred_pre.json().get("crediti_valore_beni", 0)

    # 1. Creazione Bene (POST /api/beni) con 'stato: True' (disponibile)
    payload_create = {
        "nome": nome_bene,
        "descrizione": "Un libro di testo universitario perfetto per esami",
        "id_categoria": cat_id,
        "id_proprietario": proprietario_id,
        "stato": True,
        "peso": 0.8,
    }
    res_create = await async_client.post("/api/beni", json=payload_create)
    assert res_create.status_code == 201
    bene_data = res_create.json()
    assert bene_data["nome"] == nome_bene
    bene_id = bene_data["id"]

    # 2. Verifica che i crediti del proprietario siano stati incrementati del valore della categoria
    res_cred_post = await async_client.get(f"/api/utenti/{proprietario_id}/crediti")
    assert res_cred_post.status_code == 200
    crediti_attesi = crediti_iniziali + categoria_test["crediti"]
    assert res_cred_post.json()["crediti_valore_beni"] == crediti_attesi

    # 3. Lettura per ID (GET /api/beni/:id)
    res_get = await async_client.get(f"/api/beni/{bene_id}")
    assert res_get.status_code == 200
    assert res_get.json()["descrizione"] == payload_create["descrizione"]

    # 4. Ricerca per categoria e per testo (GET /api/beni)
    res_search_cat = await async_client.get(f"/api/beni?id_categoria={cat_id}")
    assert res_search_cat.status_code == 200
    assert any(b["id"] == bene_id for b in res_search_cat.json())

    res_search_txt = await async_client.get(f"/api/beni?search={nome_bene}")
    assert res_search_txt.status_code == 200
    assert any(b["id"] == bene_id for b in res_search_txt.json())

    # 5. Eliminazione del bene con ricalcolo crediti (DELETE /api/beni/:id?id_proprietario=...)
    res_del = await async_client.delete(f"/api/beni/{bene_id}?id_proprietario={proprietario_id}")
    assert res_del.status_code == 200

    # 6. Verifica bene inesistente -> 404
    res_get_404 = await async_client.get(f"/api/beni/{bene_id}")
    assert res_get_404.status_code == 404


@pytest.mark.asyncio
async def test_bene_inesistente_404_integration(async_client: AsyncClient):
    """Verifica che la richiesta di un ID bene non esistente restituisca 404."""
    res = await async_client.get("/api/beni/999999999")
    assert res.status_code == 404
