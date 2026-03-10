#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_passo14.py — Teste automatizado do Passo 14 (OMR + Resultados)

Fluxo testado:
  1. Autentica coordenador
  2. Cria exam, configura, faz upload docx, trava
  3. Gera PDFs da turma
  4. Consulta gabarito atual (correct_label)
  5. Preenche gabarito manualmente via PATCH se vazio
  6. Simula respostas dos alunos diretamente no banco (mock OMR)
  7. Consulta resultados por turma (GET /exams/{id}/results)
  8. Baixa XLSX de resultados
  9. Baixa PDF devolutiva de um aluno
 10. Diagnóstico final

Execução:
  docker compose cp test_passo14.py api:/tmp/test_passo14.py
  docker compose exec api python /tmp/test_passo14.py
  docker compose cp api:/tmp/resultados_turma.xlsx resultados_turma.xlsx
  docker compose cp api:/tmp/devolutiva_aluno.pdf devolutiva_aluno.pdf
"""

import sys
import json
import urllib.request
import urllib.error
import urllib.parse

BASE      = "http://localhost:8000"
CLASS_ID  = 3
DOCX_PATH = "/app/storage/assets/simulado.docx"

COORD_USER = "coord@samba.local"
COORD_PASS = "coord123"
PROF_USER  = "prof.fisica@samba.local"
PROF_PASS  = "prof123"

# ──────────────────────────────────────────────────────────────────────────────
SEP  = "=" * 60
SEPM = "-" * 40

def ok(msg):  print(f"  ✓ {msg}")
def err(msg): print(f"  ✗ {msg}"); 
def hdr(msg): print(f"\n{SEP}\n  {msg}\n{SEP}")
def sub(msg): print(f"\n{SEPM}\n  {msg}\n{SEPM}")

# ──────────────────────────────────────────────────────────────────────────────
def request(method, path, token=None, data=None, json_data=None, files=None):
    url = BASE + path
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    if json_data is not None:
        body = json.dumps(json_data).encode()
        headers["Content-Type"] = "application/json"
    elif data is not None:
        body = data if isinstance(data, bytes) else data.encode()
    elif files is not None:
        # multipart simples
        boundary = b"----SAMBA_BOUNDARY"
        parts = []
        for name, (fname, fbytes, ftype) in files.items():
            parts.append(
                b"--" + boundary + b"\r\n"
                + f'Content-Disposition: form-data; name="{name}"; filename="{fname}"\r\n'.encode()
                + f"Content-Type: {ftype}\r\n\r\n".encode()
                + fbytes + b"\r\n"
            )
        body = b"".join(parts) + b"--" + boundary + b"--\r\n"
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary.decode()}"
    else:
        body = None

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            try:
                return r.status, json.loads(raw)
            except Exception:
                return r.status, raw
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw.decode(errors="replace")


# ──────────────────────────────────────────────────────────────────────────────
hdr("SAMBA — Teste Passo 14 (OMR + Resultados)")

# 1. Auth
sub("1. Autenticação")
status, resp = request("POST", "/auth/login",
    data=f"username={COORD_USER}&password={COORD_PASS}",
    json_data=None)
if status != 200 or "access_token" not in (resp if isinstance(resp, dict) else {}):
    err(f"Login falhou ({status}): {resp}")
    sys.exit(1)
TOKEN = resp["access_token"]
ok(f"Token obtido")

# 1b. Auth professor
sub("1b. Autenticação professor")
status, resp = request("POST", "/auth/login",
    data=f"username={PROF_USER}&password={PROF_PASS}",
    json_data=None)
if status != 200 or "access_token" not in (resp if isinstance(resp, dict) else {}):
    err(f"Login professor falhou ({status}): {resp}")
    sys.exit(1)
PROF_TOKEN = resp["access_token"]
ok(f"Token professor obtido")

# 2. Cria exam
sub("2. Criando exam")
status, resp = request("POST", "/exams/", token=TOKEN, json_data={
    "title": "Simulado Passo14 Teste",
    "description": "Teste automático passo 14",
    "year": 2026, "edition": 1, "options_count": 5, "answer_source": "teachers",
})
if status not in (200, 201):
    err(f"Criar exam ({status}): {resp}")
    sys.exit(1)
EXAM_ID = resp["id"]
ok(f"Exam criado → id={EXAM_ID}")

# 3. Assign
sub("3. Configurando assigns")
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

DB_URL = os.environ.get("DATABASE_URL", "postgresql://samba:samba@db:5432/samba_simulator")
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
db = Session()
try:
    db.execute(text("""
        INSERT INTO exam_teacher_assignment (exam_id, teacher_user_id, discipline_id, class_id)
        VALUES (:eid, 5, 3, :cid)
        ON CONFLICT DO NOTHING
    """), {"eid": EXAM_ID, "cid": CLASS_ID})
    db.execute(text("""
        INSERT INTO exam_class_assignment (exam_id, class_id)
        VALUES (:eid, :cid)
        ON CONFLICT DO NOTHING
    """), {"eid": EXAM_ID, "cid": CLASS_ID})
    db.commit()
    ok("Assigns criados")
except Exception as e:
    db.rollback()
    err(f"Assign falhou: {e}")

# 4. Upload docx
sub("4. Upload docx")
with open(DOCX_PATH, "rb") as f:
    docx_bytes = f.read()
# Upload multipart com class_id e discipline_id
import urllib.request as _ur
boundary = b"----SAMBA14"
parts = []
for fname2, fval in [("class_id", str(CLASS_ID).encode()), ("discipline_id", b"3")]:
    parts.append(
        b"--" + boundary + b"\r\n"
        + f'Content-Disposition: form-data; name="{fname2}"\r\n\r\n'.encode()
        + fval + b"\r\n"
    )
parts.append(
    b"--" + boundary + b"\r\n"
    + b'Content-Disposition: form-data; name="file"; filename="simulado.docx"\r\n'
    + b"Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document\r\n\r\n"
    + docx_bytes + b"\r\n"
)
body = b"".join(parts) + b"--" + boundary + b"--\r\n"
req2 = _ur.Request(
    BASE + f"/exams/{EXAM_ID}/questions/upload",
    data=body,
    headers={
        "Authorization": f"Bearer {PROF_TOKEN}",
        "Content-Type": f"multipart/form-data; boundary={boundary.decode()}",
    },
    method="POST"
)
try:
    with _ur.urlopen(req2) as r2:
        import json as _json
        resp = _json.loads(r2.read())
    status = 200
except _ur.HTTPError as e:
    status = e.code
    resp = _json.loads(e.read())
if status not in (200, 201):
    err(f"Upload ({status}): {resp}")
    sys.exit(1)
n_questions = resp.get("imported", resp.get("questoes_importadas", 0))
ok(f"Upload OK → {n_questions} questões")

# 5. Lock
sub("5. Travando exam")
status, resp = request("POST", f"/exams/{EXAM_ID}/lock", token=TOKEN)
if status not in (200, 201):
    err(f"Lock ({status}): {resp}")
    sys.exit(1)
ok("Exam locked")

# 6. Consulta gabarito atual
sub("6. Consultando gabarito")
status, links = request("GET", f"/exams/{EXAM_ID}/links", token=TOKEN)
if status != 200:
    err(f"Links ({status}): {links}")
    sys.exit(1)
ok(f"{len(links)} links encontrados")

sem_gabarito = [l for l in links if not l.get("correct_label")]
ok(f"Com gabarito: {len(links)-len(sem_gabarito)} | Sem gabarito: {len(sem_gabarito)}")

# 7. Preenche gabarito vazio via PATCH
if sem_gabarito:
    sub("7. Preenchendo gabarito vazio (PATCH)")
    OPCOES = ["A", "B", "C", "D", "E"]
    erros_patch = 0
    for i, link in enumerate(sem_gabarito):
        resposta = OPCOES[i % 5]
        status, resp = request(
            "PATCH",
            f"/exams/{EXAM_ID}/links/{link['id']}/answer?answer={resposta}",
            token=TOKEN
        )
        if status != 200:
            erros_patch += 1
    if erros_patch:
        err(f"{erros_patch} erros ao preencher gabarito")
    else:
        ok(f"{len(sem_gabarito)} gabaritos preenchidos automaticamente")
else:
    ok("7. Gabarito já completo — PATCH não necessário")

# 8. Simula respostas dos alunos diretamente no banco (mock OMR)
sub("8. Simulando respostas dos alunos (mock OMR)")
# Busca links atualizados
status, links = request("GET", f"/exams/{EXAM_ID}/links", token=TOKEN)
students = db.execute(text("SELECT id FROM students WHERE class_id=:cid ORDER BY id"), {"cid": CLASS_ID}).fetchall()
OPCOES   = ["A", "B", "C", "D", "E"]
saved = 0
try:
    for student in students:
        sid = student[0]
        for i, link in enumerate(links):
            # Simula: aluno acerta 70% das questões
            correct_label = link.get("correct_label") or "A"
            marked = correct_label if (i % 10 != 0) else OPCOES[(OPCOES.index(correct_label) + 1) % 5]
            is_correct = marked == correct_label
            db.execute(text("""
                INSERT INTO student_answers (exam_id, student_id, question_link_id, marked_label, is_correct)
                VALUES (:eid, :sid, :lid, :ml, :ic)
                ON CONFLICT (exam_id, student_id, question_link_id)
                DO UPDATE SET marked_label=EXCLUDED.marked_label, is_correct=EXCLUDED.is_correct
            """), {
                "eid": EXAM_ID, "sid": sid, "lid": link["id"],
                "ml": marked, "ic": is_correct,
            })
            saved += 1
    db.commit()
    ok(f"{saved} respostas simuladas para {len(students)} alunos")
except Exception as e:
    db.rollback()
    err(f"Mock OMR falhou: {e}")

db.close()

# 9. Consulta resultados
sub("9. Consultando resultados da turma")
status, results = request("GET", f"/exams/{EXAM_ID}/results?class_id={CLASS_ID}", token=TOKEN)
if status != 200:
    err(f"Resultados ({status}): {results}")
else:
    total = results.get("total_students", 0)
    ok(f"{total} alunos com resultado")
    if results.get("results"):
        top = results["results"][0]
        ok(f"1º lugar: {top['student_name']} — Nota: {top['nota']} — Acertos: {top['acertos']}/{top['total']}")
        last = results["results"][-1]
        ok(f"Último: {last['student_name']} — Nota: {last['nota']}")
        
        # Mostra breakdown por disciplina do primeiro aluno
        if top.get("por_disciplina"):
            print("\n  Breakdown por disciplina (1º lugar):")
            for d in top["por_disciplina"]:
                print(f"    {d['discipline_name']}: {d['acertos']}/{d['total']} → {d['nota']}")

# 10. Download XLSX
sub("10. Exportando XLSX")
status, xlsx = request("GET", f"/exams/{EXAM_ID}/results/export?class_id={CLASS_ID}", token=TOKEN)
if status != 200:
    err(f"XLSX ({status}): {xlsx}")
else:
    with open("/tmp/resultados_turma.xlsx", "wb") as f:
        f.write(xlsx if isinstance(xlsx, bytes) else b"")
    ok(f"XLSX salvo → /tmp/resultados_turma.xlsx ({len(xlsx):,} bytes)")

# 11. Download PDF devolutiva do primeiro aluno
sub("11. Exportando PDF devolutiva")
if results.get("results"):
    first_student_id = results["results"][0]["student_id"]
    status, pdf = request("GET", f"/exams/{EXAM_ID}/results/report/{first_student_id}", token=TOKEN)
    if status != 200:
        err(f"PDF devolutiva ({status}): {pdf}")
    else:
        with open("/tmp/devolutiva_aluno.pdf", "wb") as f:
            f.write(pdf if isinstance(pdf, bytes) else b"")
        ok(f"PDF salvo → /tmp/devolutiva_aluno.pdf ({len(pdf):,} bytes)")

# Diagnóstico final
print(f"\n{SEP}")
print("  DIAGNÓSTICO FINAL")
print(SEP)
print(f"  exam_id        : {EXAM_ID}")
print(f"  class_id       : {CLASS_ID}")
print(f"  questões       : {len(links)}")
print(f"  alunos         : {len(students)}")
print(f"  respostas mock : {saved}")
print(f"\n  Arquivos gerados:")
print(f"    /tmp/resultados_turma.xlsx")
print(f"    /tmp/devolutiva_aluno.pdf")
print(f"\n  Para baixar:")
print(f"    docker compose cp api:/tmp/resultados_turma.xlsx resultados_turma.xlsx")
print(f"    docker compose cp api:/tmp/devolutiva_aluno.pdf devolutiva_aluno.pdf")
print(SEP)