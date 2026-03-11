#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_integration.py — Teste de integração completo do SAMBA Simulator

Fluxo:
  0.  Reset banco + seed
  1.  Autenticação (coord + professor)
  2.  Verifica estrutura escolar criada pelo seed
  3.  Importa alunos reais via 3A.csv
  4.  Cria simulado + assigns
  5.  Upload simulado.docx (com gabarito: X)
  6.  Verifica gabarito extraído automaticamente
  7.  Lock do simulado
  8.  Gera PDFs por turma
  9.  Download caderno individual
  10. Batch cadernos / OMR / ZIP individual
  11. Simula respostas com 3 perfis (bom/médio/fraco)
  12. Resultados por turma com ranking
  13. Resultado individual por disciplina
  14. Export XLSX
  15. PDF devolutiva individual
  16. ZIP devolutivas por turma

Uso:
  docker compose cp test_integration.py api:/tmp/test_integration.py
  docker compose exec api python /tmp/test_integration.py
  docker compose exec api python /tmp/test_integration.py --no-reset
"""

from __future__ import annotations
import sys, os, io, json, time, random, zipfile, traceback
import urllib.request, urllib.error

BASE       = "http://localhost:8000"
DOCX_PATH  = "/app/storage/assets/simulado.docx"
CSV_PATH   = "/app/storage/assets/3A.csv"
CLASS_NAME = "3ªA"
DISC_NAME  = "Física"
RESET_DB   = "--no-reset" not in sys.argv
random.seed(42)

COORD_USER = "coord@samba.local"
COORD_PASS = "coord123"
PROF_USER  = "prof.fisica@samba.local"
PROF_PASS  = "prof123"

SEP  = "=" * 64
SEPM = "-" * 44
_results: list[dict] = []
_errors:  list[str]  = []

def section(t): print(f"\n{SEPM}\n  {t}\n{SEPM}")
def ok(m):   print(f"  ✓ {m}"); _results.append({"s":"ok","m":m})
def fail(m, fatal=False):
    print(f"  ✗ {m}"); _results.append({"s":"fail","m":m}); _errors.append(m)
    if fatal: _summary(); sys.exit(1)
def warn(m): print(f"  ⚠ {m}")

def _summary():
    p = sum(1 for r in _results if r["s"]=="ok")
    f = sum(1 for r in _results if r["s"]=="fail")
    print(f"\n{SEP}\n  RESULTADO: {p} ✓  |  {f} ✗")
    if _errors:
        print("\n  Falhas:")
        for e in _errors: print(f"    ✗ {e}")
    print(SEP)

def req(method, path, token=None, data=None, json_data=None, files=None,
        raw=False, params=None):
    from urllib.parse import urlencode
    url = BASE + path + ("?" + urlencode(params) if params else "")
    headers = {}
    if token: headers["Authorization"] = f"Bearer {token}"
    if json_data is not None:
        body = json.dumps(json_data).encode(); headers["Content-Type"] = "application/json"
    elif files is not None:
        boundary = b"----SAMBA_INT"
        parts = []
        for k,v in (files.get("fields") or {}).items():
            parts.append(b"--"+boundary+b"\r\n"
                +f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode()
                +str(v).encode()+b"\r\n")
        for k,(fname,fbytes,ftype) in (files.get("files") or {}).items():
            parts.append(b"--"+boundary+b"\r\n"
                +f'Content-Disposition: form-data; name="{k}"; filename="{fname}"\r\n'.encode()
                +f"Content-Type: {ftype}\r\n\r\n".encode()+fbytes+b"\r\n")
        body = b"".join(parts)+b"--"+boundary+b"--\r\n"
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary.decode()}"
    elif data is not None:
        body = data.encode() if isinstance(data,str) else data
    else:
        body = None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            rb = resp.read()
            if raw: return resp.status, rb
            try:    return resp.status, json.loads(rb)
            except: return resp.status, rb
    except urllib.error.HTTPError as e:
        rb = e.read()
        if raw: return e.code, rb
        try:    return e.code, json.loads(rb)
        except: return e.code, rb.decode(errors="replace")

print(f"\n{SEP}")
print(f"  SAMBA Simulator — Teste de Integração Completo")
print(f"  {'COM reset do banco' if RESET_DB else 'SEM reset (--no-reset)'}")
print(SEP)

# 0. Reset
if RESET_DB:
    section("0. Reset do banco + seed")
    try:
        import subprocess
        from sqlalchemy import create_engine, text
        DB_URL = os.environ.get("DATABASE_URL",
            "postgresql+psycopg2://postgres:postgres@localhost:5432/samba_simulator")
        eng = create_engine(DB_URL)
        with eng.connect() as conn:
            conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
            conn.commit()
        eng.dispose(); ok("Schema resetado")
        r = subprocess.run(["alembic","upgrade","head"], capture_output=True, text=True, cwd="/app")
        if r.returncode != 0: fail(f"alembic: {r.stderr}", fatal=True)
        ok("Migrations aplicadas")
        r2 = subprocess.run(["python","-m","app.core.seed"], capture_output=True, text=True, cwd="/app")
        if r2.returncode != 0: fail(f"Seed: {r2.stderr}", fatal=True)
        ok("Seed executado")
        time.sleep(1)
    except Exception as e:
        fail(f"Reset: {e}", fatal=True); traceback.print_exc()

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
DB_URL = os.environ.get("DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/samba_simulator")
engine = create_engine(DB_URL)
DBSess = sessionmaker(bind=engine)

# 1. Auth
section("1. Autenticação")
TOKEN = PROF_TOKEN = None
s,r = req("POST","/auth/login", data=f"username={COORD_USER}&password={COORD_PASS}")
if s==200 and isinstance(r,dict) and "access_token" in r:
    TOKEN=r["access_token"]; ok("Coordenador autenticado")
else: fail(f"Login coord ({s}): {r}", fatal=True)
s,r = req("POST","/auth/login", data=f"username={PROF_USER}&password={PROF_PASS}")
if s==200 and isinstance(r,dict) and "access_token" in r:
    PROF_TOKEN=r["access_token"]; ok("Professor autenticado")
else: fail(f"Login prof ({s}): {r}", fatal=True)

# 2. Estrutura escolar
section("2. Estrutura escolar")
db = DBSess()
try:
    row = db.execute(text("SELECT id FROM school_classes WHERE name=:n"),{"n":CLASS_NAME}).fetchone()
    if row: CLASS_ID=row[0]; ok(f"Turma '{CLASS_NAME}' → id={CLASS_ID}")
    else:   fail(f"Turma '{CLASS_NAME}' não encontrada", fatal=True)
    row = db.execute(text("SELECT id FROM disciplines WHERE name=:n"),{"n":DISC_NAME}).fetchone()
    if row: DISC_ID=row[0]; ok(f"Disciplina '{DISC_NAME}' → id={DISC_ID}")
    else:   fail(f"Disciplina '{DISC_NAME}' não encontrada", fatal=True)
    row = db.execute(text("SELECT id FROM users WHERE email=:e"),{"e":PROF_USER}).fetchone()
    if row: TEACHER_ID=row[0]; ok(f"Professor → id={TEACHER_ID}")
    else:   fail("Professor não encontrado", fatal=True)
finally: db.close()

# 3. Import CSV
section("3. Importação de alunos (3A.csv)")
try:
    with open(CSV_PATH,"rb") as f: csv_bytes=f.read()
    s,r = req("POST","/school/students/import", token=TOKEN,
        files={"files":{"file":("3A.csv",csv_bytes,"text/csv")}},
        params={"class_name":CLASS_NAME, "dry_run": "false"})
    if s in (200,201) and isinstance(r,dict):
        ok(f"Importados: {r.get('imported',r.get('created','?'))} | pulados: {r.get('skipped','?')}")
    else: fail(f"Import CSV ({s}): {r}")
except FileNotFoundError: fail(f"CSV não encontrado: {CSV_PATH}")

db = DBSess()
try:
    students = db.execute(
        text("SELECT id,name FROM students WHERE class_id=:cid ORDER BY name"),
        {"cid":CLASS_ID}).fetchall()
    ok(f"{len(students)} alunos na turma")
    STUDENT_ID = students[0][0] if students else None
finally: db.close()
if not students: fail("Nenhum aluno na turma", fatal=True)

# 4. Criar simulado
section("4. Criar simulado + assigns")
s,r = req("POST","/exams/", token=TOKEN, json_data={
    "title":"1º Simulado SAMBA 2026 — Física",
    "description":"Teste de integração",
    "year":2026,"edition":1,"options_count":5,"answer_source":"teachers"})
if s in (200,201) and isinstance(r,dict) and "id" in r:
    EXAM_ID=r["id"]; ok(f"Simulado criado → id={EXAM_ID}")
else: fail(f"Criar exam ({s}): {r}", fatal=True)

db = DBSess()
try:
    db.execute(text("""
        INSERT INTO exam_teacher_assignment (exam_id,teacher_user_id,discipline_id,class_id)
        VALUES (:eid,:tid,:did,:cid) ON CONFLICT DO NOTHING"""),
        {"eid":EXAM_ID,"tid":TEACHER_ID,"did":DISC_ID,"cid":CLASS_ID})
    db.execute(text("""
        INSERT INTO exam_class_assignment (exam_id,class_id)
        VALUES (:eid,:cid) ON CONFLICT DO NOTHING"""),
        {"eid":EXAM_ID,"cid":CLASS_ID})
    db.commit(); ok("Assigns criados")
except Exception as e: db.rollback(); fail(f"Assigns: {e}")
finally: db.close()

# 5. Upload docx
section("5. Upload simulado.docx")
try:
    with open(DOCX_PATH,"rb") as f: docx_bytes=f.read()
    s,r = req("POST",f"/exams/{EXAM_ID}/questions/upload", token=PROF_TOKEN,
        files={"fields":{"class_id":CLASS_ID,"discipline_id":DISC_ID},
               "files":{"file":("simulado.docx",docx_bytes,
                   "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}})
    if s in (200,201): ok(f"Upload OK: {r}")
    else: fail(f"Upload ({s}): {r}")
except FileNotFoundError: fail(f"DOCX não encontrado: {DOCX_PATH}")

# 6. Gabarito
section("6. Gabarito extraído automaticamente")
s,links = req("GET",f"/exams/{EXAM_ID}/links", token=TOKEN)
if s==200 and isinstance(links,list):
    com_gab = [l for l in links if l.get("correct_label")]
    sem_gab = [l for l in links if not l.get("correct_label")]
    ok(f"{len(links)} questões | com gabarito: {len(com_gab)} | sem: {len(sem_gab)}")
    if com_gab:
        sample = [(l["order_idx"]+1, l["correct_label"]) for l in com_gab[:5]]
        ok(f"Amostra: {sample}")
    if sem_gab:
        warn(f"{len(sem_gab)} sem gabarito → preenchendo via PATCH")
        OPCOES=["A","B","C","D","E"]
        for i,link in enumerate(sem_gab):
            req("PATCH",f"/exams/{EXAM_ID}/links/{link['id']}/answer?answer={OPCOES[i%5]}",token=TOKEN)
        ok(f"{len(sem_gab)} gabaritos preenchidos via PATCH")
        _,links = req("GET",f"/exams/{EXAM_ID}/links",token=TOKEN)
else: fail(f"Links ({s}): {links}"); links=[]

# 7. Lock
section("7. Lock")
s,r = req("POST",f"/exams/{EXAM_ID}/lock", token=TOKEN)
if s in (200,201): ok("Simulado LOCKED")
else: fail(f"Lock ({s}): {r}", fatal=True)

# 8. Gerar PDFs
section("8. Geração de PDFs por turma")
s,r = req("POST",f"/exams/{EXAM_ID}/pdf/generate", token=TOKEN, params={"class_id":CLASS_ID})
if s in (200,201):
    n = r.get("result",{}).get("students_count","?") if isinstance(r,dict) else "?"
    ok(f"PDFs gerados para {n} alunos")
else: fail(f"Gerar PDFs ({s}): {r}")

# 9. Download caderno individual
section("9. Download caderno individual")
s,pdf = req("GET",f"/exams/{EXAM_ID}/pdf/download", token=TOKEN, raw=True,
    params={"student_id":STUDENT_ID,"type":"booklet"})
if s==200 and isinstance(pdf,bytes) and pdf.startswith(b"%PDF"):
    with open(f"/tmp/caderno_{STUDENT_ID}.pdf","wb") as f: f.write(pdf)
    ok(f"Caderno {students[0][1].split()[0]}: {len(pdf):,} bytes → /tmp/caderno_{STUDENT_ID}.pdf")
else: fail(f"Download caderno ({s})")

NOME_ALUNO = students[0][1].split()[0].capitalize() if students else "aluno"

# 9b. Caderno individual — salva com nome do aluno
section("9b. Caderno + OMR de aluno individual")
s,omr = req("GET",f"/exams/{EXAM_ID}/pdf/download", token=TOKEN, raw=True,
    params={"student_id":STUDENT_ID,"type":"answer_sheet"})
if s==200 and isinstance(omr,bytes) and omr.startswith(b"%PDF"):
    with open(f"/tmp/omr_{NOME_ALUNO}.pdf","wb") as f: f.write(omr)
    ok(f"Folha OMR de {NOME_ALUNO}: {len(omr):,} bytes → /tmp/omr_{NOME_ALUNO}.pdf")
else:
    warn(f"OMR individual ({s}) — type 'answer_sheet' pode ser 'omr', tentando...")
    s,omr = req("GET",f"/exams/{EXAM_ID}/pdf/download", token=TOKEN, raw=True,
        params={"student_id":STUDENT_ID,"type":"omr"})
    if s==200 and isinstance(omr,bytes) and omr.startswith(b"%PDF"):
        with open(f"/tmp/omr_{NOME_ALUNO}.pdf","wb") as f: f.write(omr)
        ok(f"Folha OMR de {NOME_ALUNO}: {len(omr):,} bytes")
    else:
        fail(f"Download OMR individual ({s})")

# 10. Batch completo — cadernos, OMR e ZIP por RA
section("10. Batch por turma (cadernos / OMR / ZIP individual)")
BATCH_FILES = {}
for btype,label,magic,fname in [
    ("booklets",  "Cadernos por turma (PDF)", b"%P", "/tmp/batch_cadernos_turma.pdf"),
    ("omr",       "OMR por turma (PDF)",       b"%P", "/tmp/batch_omr_turma.pdf"),
    ("individual","ZIP por RA",                b"PK", "/tmp/batch_zip_por_ra.zip")]:
    s,data = req("GET",f"/exams/{EXAM_ID}/pdf/batch/", token=TOKEN, raw=True,
        params={"class_id":CLASS_ID,"type":btype})
    if s==200 and isinstance(data,bytes) and data[:2]==magic and len(data)>500:
        with open(fname,"wb") as f: f.write(data)
        # Conta páginas/arquivos
        if fname.endswith(".zip"):
            import zipfile as _zf, io as _io
            with _zf.ZipFile(_io.BytesIO(data)) as zf:
                n = len(zf.namelist())
            ok(f"{label}: {len(data):,} bytes | {n} arquivos → {fname}")
        else:
            ok(f"{label}: {len(data):,} bytes → {fname}")
        BATCH_FILES[btype] = fname
    else:
        fail(f"Batch {label} ({s})")

# 11. Simula respostas com 3 perfis
section("11. Simulação de respostas (3 perfis)")
OPCOES=["A","B","C","D","E"]
n_students=len(students)
perfis={}
for i,(sid,sname) in enumerate(students):
    frac=i/n_students
    if   frac<0.33: perfis[sid]=("bom",  0.88)
    elif frac<0.66: perfis[sid]=("medio",0.65)
    else:           perfis[sid]=("fraco",0.40)

db=DBSess(); saved=0
try:
    for sid,sname in students:
        perfil,taxa=perfis[sid]
        for link in links:
            correct=link.get("correct_label") or "A"
            if random.random()<taxa: marked=correct
            else: marked=random.choice([o for o in OPCOES if o!=correct])
            db.execute(text("""
                INSERT INTO student_answers (exam_id,student_id,question_link_id,marked_label,is_correct)
                VALUES (:eid,:sid,:lid,:ml,:ic)
                ON CONFLICT (exam_id,student_id,question_link_id)
                DO UPDATE SET marked_label=EXCLUDED.marked_label,is_correct=EXCLUDED.is_correct
            """),{"eid":EXAM_ID,"sid":sid,"lid":link["id"],"ml":marked,"ic":marked==correct})
            saved+=1
    db.commit()
    bons  =sum(1 for p,_ in perfis.values() if p=="bom")
    medios=sum(1 for p,_ in perfis.values() if p=="medio")
    fracos=sum(1 for p,_ in perfis.values() if p=="fraco")
    ok(f"{saved} respostas | {bons} bons (~88%) | {medios} médios (~65%) | {fracos} fracos (~40%)")
except Exception as e:
    db.rollback(); fail(f"Respostas: {e}"); traceback.print_exc()
finally: db.close()

# 12. Resultados
section("12. Resultados por turma (ranking)")
s,results=req("GET",f"/exams/{EXAM_ID}/results",token=TOKEN,params={"class_id":CLASS_ID})
if s==200 and isinstance(results,dict) and results.get("results"):
    res_list=results["results"]
    ok(f"{results['total_students']} alunos com resultado")
    print(f"\n  {'#':<4} {'Nome':<42} {'Nota':>5} {'Acertos':>9}")
    print(f"  {'-'*4} {'-'*41} {'-'*5} {'-'*9}")
    for r in res_list:
        print(f"  {r['ranking']:<4} {r['student_name'][:41]:<42} {r['nota']:>5} {r['acertos']:>4}/{r['total']:<3}")
    notas=set(r["nota"] for r in res_list)
    ok(f"{'Ranking variado ✓' if len(notas)>3 else '⚠ Pouca variação'} ({len(notas)} notas distintas)")
else:
    fail(f"Resultados ({s}): {results}"); results={"results":[]}

# 13. Individual
section("13. Resultado individual por disciplina")
s,result=req("GET",f"/exams/{EXAM_ID}/results",token=TOKEN,params={"student_id":STUDENT_ID})
if s==200 and isinstance(result,dict):
    ok(f"{result['student_name']} — {result['nota']} ({result['acertos']}/{result['total']})")
    for d in result.get("por_disciplina",[]):
        ok(f"  {d['discipline_name']}: {d['acertos']}/{d['total']} → {d['nota']}")
else: fail(f"Individual ({s}): {result}")

# 14. XLSX
section("14. Export XLSX")
s,xlsx=req("GET",f"/exams/{EXAM_ID}/results/export",token=TOKEN,raw=True,params={"class_id":CLASS_ID})
if s==200 and isinstance(xlsx,bytes) and len(xlsx)>1000:
    with open("/tmp/resultados_integracao.xlsx","wb") as f: f.write(xlsx)
    ok(f"XLSX: {len(xlsx):,} bytes")
else: fail(f"XLSX ({s})")

# 15. PDF devolutiva
section("15. PDF devolutiva individual")
s,pdf=req("GET",f"/exams/{EXAM_ID}/results/report/{STUDENT_ID}",token=TOKEN,raw=True)
if s==200 and isinstance(pdf,bytes) and pdf.startswith(b"%PDF"):
    with open("/tmp/devolutiva_integracao.pdf","wb") as f: f.write(pdf)
    ok(f"PDF devolutiva: {len(pdf):,} bytes")
else: fail(f"PDF devolutiva ({s})")

# 16. ZIP devolutivas
section("16. ZIP devolutivas por turma")
s,zdata=req("GET",f"/exams/{EXAM_ID}/results/export/reports",token=TOKEN,raw=True,params={"class_id":CLASS_ID})
if s==200 and isinstance(zdata,bytes) and len(zdata)>1000:
    with open("/tmp/devolutivas_integracao.zip","wb") as f: f.write(zdata)
    with zipfile.ZipFile(io.BytesIO(zdata)) as zf:
        n_pdfs=len([n for n in zf.namelist() if n.endswith(".pdf")])
    ok(f"ZIP: {len(zdata):,} bytes | {n_pdfs} PDFs")
else: fail(f"ZIP devolutivas ({s})")

# Resumo
_summary()
print(f"\n  exam_id={EXAM_ID} | class_id={CLASS_ID} | alunos={n_students} | questões={len(links)}")
print(f"\n  Para baixar:")
print(f"    docker compose cp api:/tmp/resultados_integracao.xlsx .")
print(f"    docker compose cp api:/tmp/devolutiva_integracao.pdf .")
print(f"    docker compose cp api:/tmp/devolutivas_integracao.zip .")
print(SEP)
sys.exit(0 if not _errors else 1)