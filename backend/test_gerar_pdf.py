"""
test_gerar_pdf.py
=================
Script de teste completo para geração de cadernos PDF no SAMBA Simulator.

Uso (dentro do container):
    python test_gerar_pdf.py

Ou via PowerShell (fora do container):
    docker compose exec api python /tmp/test_gerar_pdf.py

O script:
  1. Autentica como coord e como professor de física
  2. Cria um novo exam
  3. Faz o assign de turma/disciplina/professor
  4. Faz upload do docx de teste (/tmp/simulado.docx)
  5. Cria os ExamQuestionLinks com gabarito A
  6. Loca o exam
  7. Gera os PDFs para a turma 3ªA (class_id=3)
  8. Baixa o caderno do student_id=1 e salva em /tmp/booklet_teste.pdf
  9. Imprime resumo do resultado
"""

import sys
import json
import urllib.request
import urllib.error
import urllib.parse

# Garante que o módulo 'app' seja encontrado (container monta em /app)
sys.path.insert(0, "/app")

from app.core.db import SessionLocal
from app.models.exam import (
    ExamTeacherAssignment, ExamClassAssignment, ExamQuestionLink
)

# =============================================================================
# CONFIG
# =============================================================================
BASE_URL      = "http://localhost:8000"
COORD_EMAIL   = "coord@samba.local"
COORD_PASS    = "coord123"
PROF_EMAIL    = "prof.fisica@samba.local"
PROF_PASS     = "prof123"
TEACHER_ID    = 5
DISCIPLINE_ID = 3
CLASS_ID      = 3
DOCX_PATH     = "/app/storage/assets/simulado.docx"
OUT_PDF       = "/tmp/booklet_teste.pdf"
EXAM_TITLE    = "Teste Automatizado PDF"
EXAM_AREA     = "Ciencias da Natureza"

# =============================================================================
# HELPERS
# =============================================================================

def _req(method, path, token=None, json_body=None, form_data=None,
         multipart=None, out_file=None):
    url = BASE_URL + path
    headers = {}
    body = None

    if token:
        headers["Authorization"] = f"Bearer {token}"

    if json_body is not None:
        body = json.dumps(json_body).encode()
        headers["Content-Type"] = "application/json"

    elif form_data is not None:
        body = urllib.parse.urlencode(form_data).encode()
        # sem Content-Type — urllib usa application/x-www-form-urlencoded

    elif multipart is not None:
        boundary = "SAMBA_BOUNDARY_X"
        parts = b""
        for name, value in multipart["fields"].items():
            parts += (
                f"--{boundary}\r\n"
                f"Content-Disposition: form-data; name={name}\r\n\r\n"
                f"{value}\r\n"
            ).encode()
        fname, fbytes = multipart["file"]
        parts += (
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=file; filename={fname}\r\n"
            f"Content-Type: application/octet-stream\r\n\r\n"
        ).encode() + fbytes + f"\r\n--{boundary}--\r\n".encode()
        body = parts
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"

    req = urllib.request.Request(url, data=body, method=method, headers=headers)

    # Seguir redirect 307/308 mantendo método e body
    class _NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, h, code, msg, newurl, newheaders=None):
            new_req = urllib.request.Request(newurl, data=req.data, method=req.method)
            for k, v in req.header_items():
                if k.lower() not in ("host", "content-length"):
                    new_req.add_header(k, v)
            return new_req

    opener = urllib.request.build_opener(_NoRedirect)

    try:
        with opener.open(req) as r:
            if out_file:
                with open(out_file, "wb") as f:
                    f.write(r.read())
                return {"_saved": out_file}
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        msg = e.read().decode()
        print(f"  ✗ HTTP {e.code} — {msg[:300]}")
        sys.exit(1)


def ok(label, data=None):
    extra = ""
    if isinstance(data, dict):
        for k in ("id", "status", "detail", "created", "images_saved", "_saved"):
            if k in data:
                extra = f" → {k}={data[k]}"
                break
    print(f"  ✓ {label}{extra}")
    return data


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("\n" + "="*60)
    print("  SAMBA — Teste de Geração de PDF")
    print("="*60)

    # 1. Auth coord
    print("\n[1] Autenticando coordenador...")
    r = _req("POST", "/auth/login", form_data={
        "username": COORD_EMAIL, "password": COORD_PASS
    })
    token_coord = r["access_token"]
    ok("Token coord obtido")

    # 2. Auth professor
    print("\n[2] Autenticando professor...")
    r = _req("POST", "/auth/login", form_data={
        "username": PROF_EMAIL, "password": PROF_PASS
    })
    token_prof = r["access_token"]
    ok("Token professor obtido")

    # 3. Cria exam
    print("\n[3] Criando exam...")
    r = _req("POST", "/exams/", token=token_coord, json_body={
        "title": EXAM_TITLE,
        "area": EXAM_AREA,
        "options_count": 5,
        "answer_source": "teachers",
    })
    exam_id = r["id"]
    ok(f"Exam criado", r)

    # 4. Assign turma/disciplina/professor
    print("\n[4] Configurando assigns...")
    db = SessionLocal()
    db.add(ExamTeacherAssignment(
        exam_id=exam_id,
        teacher_user_id=TEACHER_ID,
        discipline_id=DISCIPLINE_ID,
        class_id=CLASS_ID,
    ))
    db.add(ExamClassAssignment(exam_id=exam_id, class_id=CLASS_ID))
    db.commit()
    ok(f"ExamTeacherAssignment + ExamClassAssignment criados (exam_id={exam_id})")

    # 5. Upload docx
    print("\n[5] Fazendo upload do docx...")
    with open(DOCX_PATH, "rb") as f:
        docx_bytes = f.read()
    r = _req("POST", f"/exams/{exam_id}/questions/upload/",
             token=token_prof,
             multipart={
                 "fields": {"class_id": str(CLASS_ID), "discipline_id": str(DISCIPLINE_ID)},
                 "file": ("simulado.docx", docx_bytes),
             })
    ok("Upload concluído", r)
    question_ids = r.get("question_ids", [])
    print(f"     questões importadas: {len(question_ids)} | imagens: {r.get('images_saved', 0)}")

    # 6. Cria ExamQuestionLinks
    print("\n[6] Criando links de questões (gabarito=A)...")
    for i, qid in enumerate(question_ids, 1):
        db.add(ExamQuestionLink(
            exam_id=exam_id, question_id=qid, order_idx=i, correct_label="A"
        ))
    db.commit()
    ok(f"{len(question_ids)} links criados")

    # 7. Lock
    print("\n[7] Travando exam...")
    r = _req("POST", f"/exams/{exam_id}/lock/", token=token_coord)
    ok("Exam locked", r)

    # 8. Gera PDFs para a turma
    print(f"\n[8] Gerando PDFs para turma class_id={CLASS_ID}...")
    r = _req("POST", f"/exams/{exam_id}/pdf/generate/?class_id={CLASS_ID}",
             token=token_coord)
    result = r.get("result", {})
    students_count = result.get("students_count", 0)
    ok(f"PDFs gerados para {students_count} alunos")

    # 9. Download do caderno do aluno 1
    print(f"\n[9] Baixando caderno do student_id=1 → {OUT_PDF}...")
    _req("GET", f"/exams/{exam_id}/pdf/download/?student_id=1&type=booklet",
         token=token_coord, out_file=OUT_PDF)
    ok(f"PDF salvo em {OUT_PDF}")

    db.close()

    # Resumo
    print("\n" + "="*60)
    print(f"  ✅ CONCLUÍDO — exam_id={exam_id}")
    print(f"  📄 PDF: {OUT_PDF}")
    print(f"  👥 {students_count} cadernos gerados em /app/storage/exams/{exam_id}/")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
