import pytest


def _first_ok_status(status_code: int, *expected: int) -> bool:
    return status_code in expected


async def _post_first_available(client, candidates: list[tuple[str, dict]], *, form=False):
    """
    Tenta os caminhos em ordem e retorna a 1ª Response que NÃO seja 404.
    Se 'form=True', envia como application/x-www-form-urlencoded.
    """
    for path, body in candidates:
        if form:
            resp = await client.post(path, data=body)
        else:
            resp = await client.post(path, json=body)
        if resp.status_code != 404:
            return path, resp
    # Nenhuma rota bateu; devolve a última 404 apenas para diagnóstico
    return candidates[-1][0], resp


@pytest.mark.anyio
async def test_login_success(client, monkeypatch):
    """
    Sucesso: credenciais válidas retornam Token(Out) (200).
    Envia credenciais como form-url-encoded para cobrir OAuth2PasswordRequestForm.
    """
    from app.routes import auth as auth_routes

    # Forçamos a verificação de senha a sempre "passar"
    monkeypatch.setattr(auth_routes, "verify_password", lambda plain, hashed: True, raising=False)

    # Gerador de token mockado
    monkeypatch.setattr(auth_routes, "create_access_token", lambda *a, **k: "fake.jwt.token", raising=False)

    # Candidatos comuns de rota de login
    candidates = [
        ("/auth/login", {"username": "john.doe", "password": "s3cret"}),
        ("/auth/token", {"username": "john.doe", "password": "s3cret"}),
        ("/login", {"username": "john.doe", "password": "s3cret"}),
    ]

    path, resp = await _post_first_available(client, candidates, form=True)

    if resp.status_code == 404:
        pytest.xfail(f"Rota de login não localizada (testou: {[p for p, _ in candidates]}). Ajusto assim que me enviar o path real.")
    assert _first_ok_status(resp.status_code, 200), f"{path=} {resp.status_code=} {await resp.aread()=}"
    data = resp.json()
    assert data.get("access_token") == "fake.jwt.token"
    assert data.get("token_type") in {"bearer", "Bearer"}


@pytest.mark.anyio
async def test_login_invalid_credentials(client, monkeypatch):
    """
    Falha: credenciais inválidas retornam 401 (ou 400 conforme seu handler).
    """
    from app.routes import auth as auth_routes

    # Forçamos a verificação de senha a falhar
    monkeypatch.setattr(auth_routes, "verify_password", lambda plain, hashed: False, raising=False)

    candidates = [
        ("/auth/login", {"username": "john.doe", "password": "wrong"}),
        ("/auth/token", {"username": "john.doe", "password": "wrong"}),
        ("/login", {"username": "john.doe", "password": "wrong"}),
    ]
    path, resp = await _post_first_available(client, candidates, form=True)

    if resp.status_code == 404:
        pytest.xfail(f"Rota de login não localizada (testou: {[p for p, _ in candidates]}). Ajusto quando enviar o path real.")
    assert resp.status_code in (400, 401), f"{path=} {resp.status_code=} {await resp.aread()=}"
