#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
seed_respostas.py — SAMBA Simulator
=====================================
Popula respostas simuladas de alunos para testar resultados, relatórios e OMR.

REQUISITOS:
  • Simulado deve ter questões com gabarito definido
  • Alunos devem estar cadastrados nas turmas vinculadas ao simulado

USO (dentro do container do backend):
  python seed_respostas.py --exam-id 1
  python seed_respostas.py --exam-id 1 --dry-run
  python seed_respostas.py --exam-id 1 --acertos 0.7
  python seed_respostas.py --exam-id 1 --class-id 2
  python seed_respostas.py --exam-id 1 --seed 42 --reset
"""

import argparse, os, random, sys
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Carrega .env automaticamente se existir na mesma pasta
_env = Path(__file__).parent / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

DB_URL = os.environ.get("DATABASE_URL", "postgresql://samba:samba@db:5432/samba_simulator")
engine = create_engine(DB_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

LETRAS = ["A", "B", "C", "D", "E"]
GREEN = "\033[92m"; YELLOW = "\033[93m"; RED = "\033[91m"
CYAN  = "\033[96m"; BOLD   = "\033[1m";  DIM = "\033[90m"; RESET = "\033[0m"

def c(color, s): return f"{color}{s}{RESET}"

def pick_wrong(correct, options_count):
    wrong = [l for l in LETRAS[:options_count] if l != correct]
    return random.choice(wrong) if wrong else correct

def simulate_answers(links, taxa, options_count):
    out = []
    for link in links:
        correct = link["correct_label"]
        if correct is None:
            marked = random.choice(LETRAS[:options_count])
            out.append({"question_link_id": link["id"], "marked_label": marked, "is_correct": None})
        else:
            acerta = random.random() < taxa
            marked = correct if acerta else pick_wrong(correct, options_count)
            out.append({"question_link_id": link["id"], "marked_label": marked, "is_correct": acerta})
    return out

def nota_fmt(nota):
    col = GREEN if nota >= 7 else (YELLOW if nota >= 5 else RED)
    return c(col, f"{nota:.1f}")

def bar(acertos, total, width=15):
    filled = round((acertos / total) * width) if total else 0
    return c(GREEN, "█" * filled) + c(DIM, "░" * (width - filled))

def run(exam_id, class_id, acertos, dry_run, reset):
    db = SessionLocal()
    try:
        exam = db.execute(
            text("SELECT id, title, status, options_count FROM exams WHERE id = :id"),
            {"id": exam_id},
        ).mappings().first()
        if not exam:
            print(c(RED, f"\n❌  Simulado #{exam_id} não encontrado.")); sys.exit(1)

        print(f"\n{c(BOLD, '═' * 60)}")
        print(f"  {c(BOLD, '📋  SAMBA — Seed de Respostas')}")
        print(f"{c(BOLD, '═' * 60)}")
        print(f"  Simulado : {c(CYAN, exam['title'])}  (#{exam_id})")
        print(f"  Status   : {exam['status']}  |  Alts: {exam['options_count']}")
        if dry_run: print(f"  {c(YELLOW, '⚠  DRY RUN — nada será gravado')}")
        print()

        where_class = "AND sc.id = :cid" if class_id else ""
        params = {"eid": exam_id, **({"cid": class_id} if class_id else {})}
        classes = db.execute(text(f"""
            SELECT sc.id, sc.name FROM school_classes sc
            JOIN exam_class_assignment eca ON eca.class_id = sc.id
            WHERE eca.exam_id = :eid {where_class} ORDER BY sc.name
        """), params).mappings().all()

        if not classes:
            print(c(RED, "❌  Nenhuma turma vinculada. Vincule pelo coordenador primeiro.")); sys.exit(1)

        links = db.execute(text("""
            SELECT eql.id, eql.question_id, eql.correct_label, eql.order_idx, q.discipline_id
            FROM exam_question_link eql
            JOIN questions q ON q.id = eql.question_id
            WHERE eql.exam_id = :eid ORDER BY eql.order_idx
        """), {"eid": exam_id}).mappings().all()

        if not links:
            print(c(RED, "❌  Nenhuma questão com gabarito. Preencha o gabarito primeiro.")); sys.exit(1)

        total_q = len(links)
        sem_gab = sum(1 for l in links if l["correct_label"] is None)
        opts    = exam["options_count"]

        print(f"  Questões : {total_q} total  ({sem_gab} sem gabarito)")
        print(f"  Turmas   : {', '.join(c(CYAN, cl['name']) for cl in classes)}\n")

        total_alunos = total_respostas = 0
        resumo = []

        for cls in classes:
            students = db.execute(
                text("SELECT id, name, ra FROM students WHERE class_id = :cid ORDER BY name"),
                {"cid": cls["id"]},
            ).mappings().all()

            if not students:
                print(f"  {c(YELLOW, '⚠')}  Turma '{cls['name']}' sem alunos — pulando.\n"); continue

            print(f"  {c(BOLD, '🏫 ' + cls['name'])}  ({len(students)} alunos)")
            print(f"  {'─' * 56}")

            if reset and not dry_run:
                deleted = db.execute(text("""
                    DELETE FROM student_answers WHERE exam_id = :eid
                    AND student_id IN (SELECT id FROM students WHERE class_id = :cid)
                """), {"eid": exam_id, "cid": cls["id"]}).rowcount
                if deleted: print(f"  {c(YELLOW, f'🗑  {deleted} respostas anteriores removidas')}")

            notas_turma = []

            for student in students:
                if acertos is not None:
                    taxa = acertos
                else:
                    # Beta distribution — mais alunos no meio (simula turma real)
                    taxa = min(0.98, max(0.05, random.betavariate(5, 3)))

                answers   = simulate_answers([dict(l) for l in links], taxa, opts)
                n_acertos = sum(1 for a in answers if a["is_correct"] is True)
                nota      = round((n_acertos / total_q) * 10, 2)
                notas_turma.append(nota)

                print(
                    f"  {'·' if dry_run else '✓'}  "
                    f"{student['name']:<28} "
                    f"{bar(n_acertos, total_q)}  "
                    f"{n_acertos:>2}/{total_q}  "
                    f"nota {nota_fmt(nota)}"
                )

                if not dry_run:
                    base_time = datetime.utcnow() - timedelta(hours=random.randint(1, 48))
                    for ans in answers:
                        db.execute(text("""
                            INSERT INTO student_answers
                                (exam_id, student_id, question_link_id, marked_label, is_correct, scanned_at)
                            VALUES (:eid, :sid, :qlid, :ml, :ic, :sat)
                            ON CONFLICT (exam_id, student_id, question_link_id)
                            DO UPDATE SET
                                marked_label = EXCLUDED.marked_label,
                                is_correct   = EXCLUDED.is_correct,
                                scanned_at   = EXCLUDED.scanned_at
                        """), {
                            "eid": exam_id, "sid": student["id"],
                            "qlid": ans["question_link_id"], "ml": ans["marked_label"],
                            "ic": ans["is_correct"],
                            "sat": base_time + timedelta(seconds=random.randint(0, 300)),
                        })
                        total_respostas += 1

                total_alunos += 1

            if notas_turma:
                media  = round(sum(notas_turma) / len(notas_turma), 2)
                melhor = max(notas_turma)
                pior   = min(notas_turma)
                aprov  = sum(1 for n in notas_turma if n >= 5)
                print(f"\n  {'─' * 56}")
                print(
                    f"  Média {nota_fmt(media)}  |  "
                    f"Melhor {nota_fmt(melhor)}  |  "
                    f"Pior {nota_fmt(pior)}  |  "
                    f"Aprovados {c(GREEN, str(aprov))}/{len(notas_turma)}"
                )
                resumo.append({"name": cls["name"], "media": media, "aprov": aprov, "total": len(notas_turma)})
            print()

        # Promove status para 'generated' para a página de resultados funcionar
        if not dry_run and exam["status"] in ("locked", "collecting", "review", "draft"):
            db.execute(text("UPDATE exams SET status = 'generated' WHERE id = :id"), {"id": exam_id})
            print(f"  {c(GREEN, '✓')}  Status → {c(CYAN, 'generated')}  (necessário para exibir resultados)\n")

        if not dry_run:
            db.commit()

        print(f"{c(BOLD, '═' * 60)}")
        if dry_run:
            print(f"  {c(YELLOW, '⚠  DRY RUN — nenhum dado foi gravado.')}")
        else:
            print(f"  {c(GREEN, '🎉 Seed concluído!')}")
            print(f"  Alunos      : {c(BOLD, str(total_alunos))}")
            print(f"  Respostas   : {c(BOLD, str(total_respostas))}")

        if resumo:
            print(f"\n  {c(BOLD, 'Resumo por turma:')}")
            for t in resumo:
                print(f"    • {t['name']:<22} média {nota_fmt(t['media'])}  ({t['aprov']}/{t['total']} aprovados)")

        print(f"\n  {c(BOLD, 'Endpoints:')}")
        print(f"    GET /exams/{exam_id}/results?class_id=<id>")
        print(f"    GET /exams/{exam_id}/results/summary")
        print(f"    GET /exams/{exam_id}/results/export?class_id=<id>   → XLSX")
        print(f"    GET /exams/{exam_id}/results/report/<student_id>    → PDF devolutiva")
        print(f"{c(BOLD, '═' * 60)}\n")

    except Exception as e:
        db.rollback()
        print(c(RED, f"\n💥 Erro: {e}"))
        import traceback; traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed de respostas simuladas — SAMBA Simulator")
    parser.add_argument("--exam-id",  type=int, required=True,  help="ID do simulado")
    parser.add_argument("--class-id", type=int, default=None,   help="Turma específica (padrão: todas)")
    parser.add_argument("--acertos",  type=float, default=None, help="Taxa fixa 0.0–1.0 (padrão: distribuição aleatória)")
    parser.add_argument("--dry-run",  action="store_true",      help="Simula sem gravar")
    parser.add_argument("--reset",    action="store_true",      help="Remove respostas anteriores antes de inserir")
    parser.add_argument("--seed",     type=int, default=None,   help="Seed do random (reprodutível)")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)
        print(c(CYAN, f"\n🎲  Usando seed={args.seed}"))

    if args.acertos is not None and not (0.0 <= args.acertos <= 1.0):
        print(c(RED, "❌  --acertos deve ser entre 0.0 e 1.0")); sys.exit(1)

    run(exam_id=args.exam_id, class_id=args.class_id, acertos=args.acertos, dry_run=args.dry_run, reset=args.reset)