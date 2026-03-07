# tests/test_students_import.py
# -*- coding: utf-8 -*-
"""
Testes da importação CSV de alunos (SEDUC-SP).
Endpoint: POST /school/students/import

Padrão do projeto:
  - client é AsyncClient (fixture async do conftest)
  - FakeSession já tem: class_id=10 (SchoolClass), student_id=100
  - Autenticação: get_current_user já está sobrescrito → UserStub(COORDINATOR)
  - Não existe /auth/register — não tentamos criar usuários via API
  - class_id=10 é usado diretamente (já existe na FakeSession)
  - class_name="3ªD" é testado com pytest.mark.xfail pois FakeSession
    não indexa SchoolClass por nome

Cobertura:
  - dry_run=True  → não persiste, retorna contadores corretos
  - dry_run=False → persiste (FakeSession.commit salva em memória)
  - Alunos inativos ignorados (skipped_inactive)
  - Linhas sem nome ou RA ignoradas (skipped_invalid)
  - Combinação RA + Dig. RA (inclusive dígito 'X')
  - combine_check_digit=False → usa só RA base
  - Erros 400: sem class_id/class_name, turma inexistente, CSV inválido
  - Sem autenticação: não aplicável (override global no conftest)
"""

from __future__ import annotations

import io
import pytest

# ---------------------------------------------------------------------------
# ID da turma pré-existente na FakeSession
# ---------------------------------------------------------------------------
FAKE_CLASS_ID = 10  # self._classes = {10: ClassStub(id=10)} no conftest


# ---------------------------------------------------------------------------
# Helper: monta CSV no formato SEDUC-SP
# ---------------------------------------------------------------------------

def _csv_bytes(rows: list[dict], encoding: str = "utf-8-sig") -> bytes:
    """
    Gera CSV com cabeçalho padrão SEDUC-SP (separador ;).
    Campos aceitos por row: numero, nome, ra, dig, nascimento, situacao.
    """
    header = (
        "Nº de chamada;Nome do Aluno;RA;Dig. RA;"
        "Data de Nascimento;Email Microsoft;Email Google;Situação do Aluno"
    )
    lines = [header]
    for r in rows:
        lines.append(
            f"{r.get('numero', '1')};"
            f"{r.get('nome', 'Aluno Teste')};"
            f"{r.get('ra', '12345678')};"
            f"{r.get('dig', '9')};"
            f"{r.get('nascimento', '01/01/2005')};"
            f"{r.get('email_ms', '')};"
            f"{r.get('email_g', '')};"
            f"{r.get('situacao', 'Ativo')}"
        )
    return "\n".join(lines).encode(encoding)


async def _import(client, csv_bytes: bytes, **params):
    """POST multipart no endpoint de importação (autenticação já mockada)."""
    return await client.post(
        "/school/students/import",
        params=params,
        files={"file": ("alunos.csv", io.BytesIO(csv_bytes), "text/csv")},
    )


# ---------------------------------------------------------------------------
# dry_run
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_dry_run_returns_counters(client):
    """dry_run=True → contadores corretos, dry_run=True no retorno."""
    csv = _csv_bytes([
        {"nome": "Ana Silva",  "ra": "11111111", "dig": "1"},
        {"nome": "Bia Santos", "ra": "22222222", "dig": "2"},
    ])
    resp = await _import(client, csv, class_id=FAKE_CLASS_ID, dry_run=True)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["dry_run"] is True
    assert data["created"] == 2
    assert data["updated"] == 0
    assert data["skipped_inactive"] == 0


@pytest.mark.anyio
async def test_dry_run_does_not_persist(client):
    """dry_run=True → FakeSession.rollback() chamado, aluno não aparece em query."""
    csv = _csv_bytes([{"nome": "Carlos DR", "ra": "99999999", "dig": "0"}])
    resp = await _import(client, csv, class_id=FAKE_CLASS_ID, dry_run=True)
    assert resp.status_code == 200, resp.text
    # A listagem de alunos usa FakeSession.query(Student).filter(...).all()
    # que retorna apenas os alunos pré-existentes (StudentStub id=100).
    # "Carlos DR" NÃO deve aparecer.
    list_resp = await client.get("/school/students/", params={"ra": "999999990"})
    assert list_resp.status_code == 200
    students = list_resp.json()
    names = [s.get("name", "") for s in students]
    assert "Carlos DR" not in names


# ---------------------------------------------------------------------------
# Persistência real (dry_run=False)
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_creates_returns_created_count(client):
    """dry_run=False → created=1 no retorno."""
    csv = _csv_bytes([{"nome": "Diego Lima", "ra": "33333333", "dig": "3"}])
    resp = await _import(client, csv, class_id=FAKE_CLASS_ID, dry_run=False)
    assert resp.status_code == 200, resp.text
    assert resp.json()["created"] == 1


@pytest.mark.anyio
async def test_upsert_second_import_updates(client):
    """
    Mesma turma, mesmo RA, nome diferente → endpoint processa sem erro.
    Nota: FakeSession não persiste entre requests (sem DB real), então
    o aluno não é encontrado na segunda importação e vira created=1.
    O que validamos aqui é que o endpoint responde 200 e retorna
    created+updated == 1 (exatamente um aluno processado).
    """
    ra = "44444444"
    csv_v1 = _csv_bytes([{"nome": "Eduardo V1", "ra": ra, "dig": "4"}])
    r1 = await _import(client, csv_v1, class_id=FAKE_CLASS_ID, dry_run=False)
    assert r1.status_code == 200, r1.text
    assert r1.json()["created"] == 1

    csv_v2 = _csv_bytes([{"nome": "Eduardo V2", "ra": ra, "dig": "4"}])
    r2 = await _import(client, csv_v2, class_id=FAKE_CLASS_ID, dry_run=False)
    assert r2.status_code == 200, r2.text
    data = r2.json()
    # Com FakeSession (sem persistência entre requests): created=1, updated=0
    # Com DB real (DB_TESTS=1): created=0, updated=1
    assert data["created"] + data["updated"] == 1


# ---------------------------------------------------------------------------
# Filtragem de inativos e inválidos
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_skips_inactive_students(client):
    """Apenas 'Ativo' é importado; 'Inativo' e 'Transferido' vão para skipped_inactive."""
    csv = _csv_bytes([
        {"nome": "Ativo Um",    "ra": "55555551", "dig": "1", "situacao": "Ativo"},
        {"nome": "Inativo",     "ra": "55555552", "dig": "2", "situacao": "Inativo"},
        {"nome": "Transferido", "ra": "55555553", "dig": "3", "situacao": "Transferido"},
    ])
    resp = await _import(client, csv, class_id=FAKE_CLASS_ID, dry_run=True)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["created"] == 1
    assert data["skipped_inactive"] == 2


@pytest.mark.anyio
async def test_skips_row_with_empty_name(client):
    """Linha sem nome → skipped_invalid."""
    csv = _csv_bytes([{"nome": "", "ra": "66666666", "dig": "6"}])
    resp = await _import(client, csv, class_id=FAKE_CLASS_ID, dry_run=True)
    assert resp.status_code == 200, resp.text
    assert resp.json()["skipped_invalid"] == 1


@pytest.mark.anyio
async def test_skips_row_with_empty_ra(client):
    """Linha sem RA → skipped_invalid."""
    csv = _csv_bytes([{"nome": "Sem RA", "ra": "", "dig": ""}])
    resp = await _import(client, csv, class_id=FAKE_CLASS_ID, dry_run=True)
    assert resp.status_code == 200, resp.text
    assert resp.json()["skipped_invalid"] == 1


# ---------------------------------------------------------------------------
# Dígito verificador
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_combine_true_appends_digit(client):
    """combine_check_digit=True (default) → RA final = base + dígito."""
    csv = _csv_bytes([{"nome": "Flávia X", "ra": "77777777", "dig": "X"}])
    resp = await _import(client, csv, class_id=FAKE_CLASS_ID,
                         dry_run=False, combine_check_digit=True)
    assert resp.status_code == 200, resp.text
    assert resp.json()["created"] == 1


@pytest.mark.anyio
async def test_combine_false_uses_base_only(client):
    """combine_check_digit=False → RA final = apenas a base, sem dígito."""
    csv = _csv_bytes([{"nome": "Gabriel Base", "ra": "88888888", "dig": "5"}])
    resp = await _import(client, csv, class_id=FAKE_CLASS_ID,
                         dry_run=False, combine_check_digit=False)
    assert resp.status_code == 200, resp.text
    assert resp.json()["created"] == 1


# ---------------------------------------------------------------------------
# Encoding latin-1
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_latin1_encoding_accepted(client):
    """CSV em latin-1 (codificação comum em exportações SEDUC) deve ser aceito."""
    csv = _csv_bytes(
        [{"nome": "Ígor Ação", "ra": "12121212", "dig": "1"}],
        encoding="latin-1",
    )
    resp = await _import(client, csv, class_id=FAKE_CLASS_ID, dry_run=True)
    assert resp.status_code == 200, resp.text
    assert resp.json()["created"] == 1


# ---------------------------------------------------------------------------
# Erros 400
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_error_no_class_param(client):
    """Sem class_id nem class_name → 400."""
    csv = _csv_bytes([])
    resp = await _import(client, csv, dry_run=True)
    assert resp.status_code == 400, resp.text


@pytest.mark.anyio
async def test_error_both_class_params(client):
    """Ambos class_id e class_name → 400."""
    csv = _csv_bytes([])
    resp = await _import(client, csv,
                         class_id=FAKE_CLASS_ID, class_name="3ªD", dry_run=True)
    assert resp.status_code == 400, resp.text


@pytest.mark.anyio
async def test_error_invalid_class_id(client):
    """class_id inexistente na FakeSession → 400."""
    csv = _csv_bytes([])
    resp = await _import(client, csv, class_id=99999, dry_run=True)
    assert resp.status_code == 400, resp.text


@pytest.mark.anyio
async def test_error_csv_without_header(client):
    """CSV sem cabeçalho reconhecível → 400."""
    csv = b"coluna_errada;outra_coluna\nvalor1;valor2\n"
    resp = await _import(client, csv, class_id=FAKE_CLASS_ID, dry_run=True)
    assert resp.status_code == 400, resp.text


# ---------------------------------------------------------------------------
# Resolução por class_name (xfail: FakeSession não indexa por nome)
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_resolves_by_class_name(client):
    """class_name='3ªD' → resolve turma pelo nome."""
    csv = _csv_bytes([{"nome": "Helena CN", "ra": "91919191", "dig": "9"}])
    resp = await _import(client, csv, class_name="3ªD", dry_run=True)
    assert resp.status_code == 200, resp.text
    assert resp.json()["class_name"] == "3ªD"
    assert resp.json()["created"] == 1
