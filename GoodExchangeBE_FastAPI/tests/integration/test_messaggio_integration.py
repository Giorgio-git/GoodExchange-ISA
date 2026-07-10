import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_messaggio_flusso_completo_integration(
    async_client: AsyncClient,
    utente_proprietario: dict,
    utente_beneficiario: dict,
    bene_test: dict,
):
    """
    Verifica l'invio, ricezione, ricerca per mittente/destinatario/tipo e cancellazione di un messaggio.
    """
    id_mittente = utente_beneficiario["id"]
    id_destinatario = utente_proprietario["id"]
    id_bene = bene_test["id"]

    payload = {
        "id_mittente": id_mittente,
        "id_destinatario": id_destinatario,
        "titolo": "Richiesta info su bene",
        "contenuto": "Ciao, vorrei sapere se il bene è disponibile da lunedì prossimo.",
        "tipo": "prestito",
        "id_riferito": id_bene,
    }

    # 1. Creazione (POST /api/messaggi)
    res_create = await async_client.post("/api/messaggi", json=payload)
    assert res_create.status_code == 201
    msg_id = res_create.json()["id"]

    # 2. Lettura per ID (GET /api/messaggi/:id)
    res_get = await async_client.get(f"/api/messaggi/{msg_id}")
    assert res_get.status_code == 200
    assert res_get.json()["contenuto"] == payload["contenuto"]

    # 3. Lettura per mittente (GET /api/messaggi/mittente/:id)
    res_mittente = await async_client.get(f"/api/messaggi/mittente/{id_mittente}")
    assert res_mittente.status_code == 200
    assert any(m["id"] == msg_id for m in res_mittente.json())

    # 4. Lettura per destinatario (GET /api/messaggi/destinatario/:id)
    res_destinatario = await async_client.get(
        f"/api/messaggi/destinatario/{id_destinatario}"
    )
    assert res_destinatario.status_code == 200
    assert any(m["id"] == msg_id for m in res_destinatario.json())

    # 5. Lettura per tipo e id_riferito (GET /api/messaggi/tipo/:tipo?id_riferito=...)
    res_tipo = await async_client.get(
        f"/api/messaggi/tipo/prestito?id_riferito={id_bene}"
    )
    assert res_tipo.status_code == 200
    assert any(m["id"] == msg_id for m in res_tipo.json())

    # 6. Eliminazione (DELETE /api/messaggi/:id)
    res_del = await async_client.delete(f"/api/messaggi/{msg_id}")
    assert res_del.status_code == 200

    # 7. Verifica eliminazione (GET /api/messaggi/:id -> 404)
    res_get_404 = await async_client.get(f"/api/messaggi/{msg_id}")
    assert res_get_404.status_code == 404
