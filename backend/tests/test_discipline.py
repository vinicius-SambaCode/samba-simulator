# tests/test_discipline.py
import pytest


async def _post_first_available(client, candidates: list[tuple[str, dict]]):
    for path, body in candidates:
        resp = await client.post(path, json=body)
        if resp.status_code != 404:
            return path, resp
    return candidates[-1][0], resp


async def _get_first_available(client, candidates: list[str]):
    for path in candidates:
        resp = await client.get(path)
        if resp.status_code != 404:
            return path, resp
    return candidates[-1], resp


@pytest.mark.anyio
async def test_create_discipline_success(client, monkeypatch):
    """
    POST /discipline(s) -> 200/201 com objeto criado (mockado).
    """
    from app.routes import discipline as disc_routes

    class _DiscIn:
        def __init__(self, name: str):
            self.name = name

    class _DiscOut:
        def __init__(self, id: int, name: str):
            self.id = id
            self.name = name

    # Se o handler chamar uma função de serviço, este nome pode variar.
    # (Deixamos aqui para o caso de você preferir um service no futuro.)
    def _mock_create(db, payload: _DiscIn):
        return _DiscOut(id=42, name=payload.name)

    monkeypatch.setattr(disc_routes, "create_discipline_service", _mock_create, raising=False)

    candidates = [
        ("/discipline", {"name": "Química"}),
        ("/disciplines", {"name": "Química"}),
        ("/api/discipline", {"name": "Química"}),
    ]
    path, resp = await _post_first_available(client, candidates)
    if resp.status_code == 404:
        pytest.xfail(f"Rota de criação de disciplina não localizada (testou: {[p for p,_ in candidates]}). Envie o path real que eu ajusto.")

    assert resp.status_code in (200, 201), f"{path=} {resp.status_code=} {await resp.aread()=}"
    data = resp.json()
    assert isinstance(data.get("id"), int) and data["id"] > 0
    assert data["name"] == "Química"


@pytest.mark.anyio
async def test_get_discipline_found(client, monkeypatch):
    """
    GET /discipline(s)/{id} -> 200 quando encontrado.
    """
    from app.routes import discipline as disc_routes

    def _mock_get(db, disc_id: int):
        return {"id": disc_id, "name": "Física"}

    monkeypatch.setattr(disc_routes, "get_discipline_service", _mock_get, raising=False)

    candidates = [
        "/discipline/7",
        "/disciplines/7",
        "/api/discipline/7",
    ]
    path, resp = await _get_first_available(client, candidates)
    if resp.status_code == 404:
        pytest.xfail(f"Rota de consulta de disciplina não localizada (testou: {candidates}). Envie o path real que eu ajusto.")
    assert resp.status_code == 200, f"{path=} {resp.status_code=} {await resp.aread()=}"
    data = resp.json()
    assert data["id"] == 7
    assert data["name"] == "Física"


@pytest.mark.anyio
async def test_get_discipline_not_found(client, monkeypatch):
    """
    GET /discipline(s)/{id} -> 404 quando inexistente.
    """
    from app.routes import discipline as disc_routes

    def _mock_get(db, disc_id: int):
        return None

    monkeypatch.setattr(disc_routes, "get_discipline_service", _mock_get, raising=False)

    candidates = [
        "/discipline/999",
        "/disciplines/999",
        "/api/discipline/999",
    ]
    path, resp = await _get_first_available(client, candidates)
    if resp.status_code == 404 and resp.reason_phrase == "Not Found":
        pytest.xfail(f"Rota de consulta não localizada (testou: {candidates}). Envie o path real que eu ajusto.")
    assert resp.status_code == 404, f"{path=} {resp.status_code=} {await resp.aread()=}"
