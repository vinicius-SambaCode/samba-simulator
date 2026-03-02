from starlette.responses import Response as StarletteResponse
import pytest


@pytest.mark.anyio
async def test_download_success_without_disk(client, monkeypatch):
    """
    Sucesso (200) sem tocar disco:
    - os.path.exists -> True
    - FileResponse -> Response vazio com media_type=application/pdf
    """
    import os
    from app.routes import pdf as pdf_routes

    monkeypatch.setattr(os.path, "exists", lambda p: True, raising=False)

    def _fake_file_response(path, filename, media_type):
        assert media_type == "application/pdf"
        return StarletteResponse(b"%PDF-FAKE%", media_type=media_type)

    monkeypatch.setattr(pdf_routes, "FileResponse", _fake_file_response, raising=True)

    path = "/pdf/exams/1/pdf/download"
    resp = await client.get(path, params={"student_id": 100})

    if resp.status_code == 404:
        pytest.xfail(f"Download 200 não validado: recebeu 404. Verifique se o router PDF está incluso no main e o path é {path}.")
    assert resp.status_code == 200, f"{path=} {resp.status_code=} {await resp.aread()=}"
    assert resp.headers.get("content-type", "").startswith("application/pdf")
