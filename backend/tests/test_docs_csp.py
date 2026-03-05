# backend/tests/test_docs_csp.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_openapi_version_is_3_0_3():
    r = client.get("/_openapi.json")
    assert r.status_code == 200
    data = r.json()
    assert data.get("openapi") == "3.0.3"


def test_docs_has_no_external_cdn_and_uses_local_assets():
    r = client.get("/docs")
    assert r.status_code == 200
    html = r.text

    # Não pode conter domínios externos
    assert "cdn.jsdelivr" not in html
    assert "fastapi.tiangolo.com" not in html
    assert "unpkg.com" not in html

    # Deve referenciar os assets locais
    assert "/static/swagger/swagger-ui-bundle.js" in html
    assert "/static/swagger/swagger-ui.css" in html

    # Os assets locais devem responder 200
    js = client.get("/static/swagger/swagger-ui-bundle.js")
    css = client.get("/static/swagger/swagger-ui.css")
    ico = client.get("/static/swagger/favicon-32x32.png")

    assert js.status_code == 200
    assert css.status_code == 200
    assert ico.status_code == 200
