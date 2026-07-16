"""Test di integrazione per preferiti e preferiti_item router."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_preferiti_flusso_completo_integration(
    async_client: AsyncClient,
    utente_proprietario: dict,
    utente_beneficiario: dict,
):
    """
    Verifica il flusso completo della lista preferiti con Lazy Creation:
    GET (scatena lazy creation nel DB se non esiste) → POST item → GET items → DELETE item → DELETE lista
    """
    id_utente = utente_proprietario["id"]
    id_preferito = utente_beneficiario["id"]

    # 1. GET lista preferiti (scatena lazy creation su prima richiesta)
    res_get = await async_client.get(f"/api/preferiti/{id_utente}")
    assert res_get.status_code == 200
    lista = res_get.json()
    id_lista = lista["id"] if isinstance(lista, dict) else lista[0]["id"]

    # 2. GET items (lista vuota inizialmente)
    res_items = await async_client.get(f"/api/preferitiItem/{id_lista}")
    assert res_items.status_code == 200

    # 3. POST — aggiunge utente_beneficiario ai preferiti
    res_add = await async_client.post(
        f"/api/preferitiItem/{id_lista}/{id_preferito}"
    )
    assert res_add.status_code == 201
    assert "aggiunto" in res_add.json()["messaggio"].lower()

    # 4. GET items — verifica che l'utente sia stato aggiunto
    res_items_post = await async_client.get(f"/api/preferitiItem/{id_lista}")
    assert res_items_post.status_code == 200

    # 5. DELETE item
    res_remove = await async_client.delete(
        f"/api/preferitiItem/{id_lista}/{id_preferito}"
    )
    assert res_remove.status_code == 200
    assert "rimosso" in res_remove.json()["messaggio"].lower()

    # 6. DELETE lista preferiti
    res_del = await async_client.delete(f"/api/preferiti/{id_utente}")
    assert res_del.status_code == 200


@pytest.mark.asyncio
async def test_preferiti_item_rimozione_inesistente_404(
    async_client: AsyncClient, utente_proprietario: dict
):
    """Verifica che la rimozione di un item inesistente restituisca 404."""
    res_get = await async_client.get(f"/api/preferiti/{utente_proprietario['id']}")
    lista = res_get.json()
    id_lista = lista["id"] if isinstance(lista, dict) else lista[0]["id"]

    res = await async_client.delete(f"/api/preferitiItem/{id_lista}/999999")
    assert res.status_code == 404
