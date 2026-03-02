# app/services/pdf_generator.py
# -*- coding: utf-8 -*-
"""
Gerador de PDFs (Sprint 2):
- Caderno (ABNT) com capa, sumário opcional e questões
- Cartão-resposta OMR com fiduciais, QR Code e bolhas A-D/A-E

Decisões:
- A4 (595 x 842 pt)
- Margens ~ 72 pt (próximo de 2,5 cm)
- Fontes padrão do ReportLab: Times/Helvetica (compatibilidade ampla)
- QR: reportlab.graphics.barcode.qr
- Storage local: storage/exams/{exam_id}/...

Uso principal via routes/pdf.py
"""

import os
from typing import List, Optional, Dict

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr

from sqlalchemy.orm import Session

from app.models.exam import Exam, ExamQuestionLink, Question, QuestionOption
from app.models.school import Student


# ------------------------------------------------------------------------------
# Pastas de saída (você pode parametrizar por settings)
# ------------------------------------------------------------------------------
def _exam_storage_dir(exam_id: int) -> str:
    base = os.path.join("storage", "exams", str(exam_id))
    os.makedirs(base, exist_ok=True)
    return base


# ------------------------------------------------------------------------------
# Utilitários de layout
# ------------------------------------------------------------------------------
PAGE_W, PAGE_H = A4
MARGIN = 72.0  # ~2,5 cm
TEXT_W = PAGE_W - 2 * MARGIN

HEADER_H = 60.0
FOOTER_H = 40.0
LINE_SPACING = 14.0

# OMR
FIDUCIAL_SIZE = 28.0  # ~10 mm
BUBBLE_DIAM = 17.0    # ~6 mm
BUBBLE_R = BUBBLE_DIAM / 2.0
BUBBLE_SPACING_V = 24.0
BUBBLE_SPACING_H = 32.0


def _draw_header(c: canvas.Canvas, title: str, subtitle: str = "", logo_path: Optional[str] = None):
    """
    Cabeçalho padrão: logo opcional à esquerda, texto centralizado.
    """
    y_top = PAGE_H - MARGIN + 30
    if logo_path and os.path.exists(logo_path):
        try:
            img = ImageReader(logo_path)
            # altura de ~40 pt, preservando aspeto
            c.drawImage(img, MARGIN, PAGE_H - MARGIN + 5, width=80, height=40, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(PAGE_W / 2.0, y_top, title)

    if subtitle:
        c.setFont("Helvetica", 10)
        c.drawCentredString(PAGE_W / 2.0, y_top - 16, subtitle)

    # linha
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(MARGIN, PAGE_H - MARGIN, PAGE_W - MARGIN, PAGE_H - MARGIN)


def _draw_footer(c: canvas.Canvas, exam_code: str, page_num: int):
    """
    Rodapé: numeração e código do simulado.
    """
    y = MARGIN - 40
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN, y, f"Código: {exam_code}")
    c.drawRightString(PAGE_W - MARGIN, y, f"Página {page_num}")


def _wrap_text(text: str, max_width: float, c: canvas.Canvas, font_name: str = "Times-Roman", font_size: int = 12) -> List[str]:
    """
    Quebra simples por palavras. (Suficiente para Sprint 2)
    """
    c.setFont(font_name, font_size)
    words = text.split()
    if not words:
        return [""]
    lines = []
    current = words[0]
    for w in words[1:]:
        if c.stringWidth(current + " " + w, font_name, font_size) <= max_width:
            current = current + " " + w
        else:
            lines.append(current)
            current = w
    lines.append(current)
    return lines


# ------------------------------------------------------------------------------
# Caderno (booklet)
# ------------------------------------------------------------------------------
def generate_exam_booklet_for_student(
    db: Session,
    exam: Exam,
    student: Student,
    logo_path: Optional[str] = None
) -> str:
    """
    Gera o caderno do aluno (PDF) com base nas questões do Exam.
    - Usa a ordem da seleção (ExamQuestionLink.order_idx)
    - Cabeçalho ABNT minimalista
    - Retorna o path do PDF gerado
    """
    out_dir = _exam_storage_dir(exam.id)
    out_path = os.path.join(out_dir, f"booklet_exam{exam.id}_student{student.id}.pdf")

    c = canvas.Canvas(out_path, pagesize=A4)
    page_num = 1

    # CAPA
    _draw_header(c, title="Caderno de Prova", subtitle=exam.title or "", logo_path=logo_path)
    c.setFont("Times-Roman", 18)
    c.drawCentredString(PAGE_W / 2.0, PAGE_H / 2.0 + 30, "Simulado")
    c.setFont("Times-Roman", 12)
    c.drawCentredString(PAGE_W / 2.0, PAGE_H / 2.0, f"Aluno: {student.name}  |  RA: {student.ra}")
    c.drawCentredString(PAGE_W / 2.0, PAGE_H / 2.0 - 18, f"Turma: {student.school_class.name}")
    _draw_footer(c, exam_code=f"EXAM-{exam.id}", page_num=page_num)
    c.showPage()
    page_num += 1

    # PÁGINA DE QUESTÕES
    _draw_header(c, title=exam.title or "Simulado", subtitle=exam.area or "", logo_path=logo_path)

    y = PAGE_H - MARGIN - HEADER_H
    c.setFont("Times-Roman", 12)

    # Seleção ordenada
    selection = db.query(ExamQuestionLink).filter(ExamQuestionLink.exam_id == exam.id).order_by(ExamQuestionLink.order_idx.asc()).all()
    if not selection:
        # fallback: todas as questões ordenadas por id
        selection = []
        for q in db.query(Question).filter(Question.exam_id == exam.id).order_by(Question.id).all():
            selection.append(ExamQuestionLink(exam_id=exam.id, question_id=q.id, order_idx=0))

    n = 1
    for link in selection:
        q = db.get(Question, link.question_id)
        if not q:
            continue

        # enunciado
        enun = f"{n}) {q.stem}"
        lines = _wrap_text(enun, TEXT_W, c, font_size=12)
        for ln in lines:
            if y < MARGIN + FOOTER_H + 80:
                _draw_footer(c, exam_code=f"EXAM-{exam.id}", page_num=page_num)
                c.showPage()
                page_num += 1
                _draw_header(c, title=exam.title or "Simulado", subtitle=exam.area or "", logo_path=logo_path)
                y = PAGE_H - MARGIN - HEADER_H
                c.setFont("Times-Roman", 12)
            c.drawString(MARGIN, y, ln)
            y -= LINE_SPACING

        # alternativas
        opts = db.query(QuestionOption).filter(QuestionOption.question_id == q.id).order_by(QuestionOption.label.asc()).all()
        for opt in opts:
            text = f"({opt.label}) {opt.text}"
            opt_lines = _wrap_text(text, TEXT_W - 20, c)
            for ln in opt_lines:
                if y < MARGIN + FOOTER_H + 60:
                    _draw_footer(c, exam_code=f"EXAM-{exam.id}", page_num=page_num)
                    c.showPage()
                    page_num += 1
                    _draw_header(c, title=exam.title or "Simulado", subtitle=exam.area or "", logo_path=logo_path)
                    y = PAGE_H - MARGIN - HEADER_H
                    c.setFont("Times-Roman", 12)
                c.drawString(MARGIN + 20, y, ln)
                y -= LINE_SPACING

        y -= LINE_SPACING / 2
        n += 1

    _draw_footer(c, exam_code=f"EXAM-{exam.id}", page_num=page_num)
    c.save()
    return out_path


# ------------------------------------------------------------------------------
# Cartão OMR (answer sheet)
# ------------------------------------------------------------------------------
def _draw_fiducials(c: canvas.Canvas):
    # Top-left
    c.setFillColor(colors.black)
    c.rect(MARGIN, PAGE_H - MARGIN - FIDUCIAL_SIZE, FIDUCIAL_SIZE, FIDUCIAL_SIZE, fill=True, stroke=False)
    # Top-right
    c.rect(PAGE_W - MARGIN - FIDUCIAL_SIZE, PAGE_H - MARGIN - FIDUCIAL_SIZE, FIDUCIAL_SIZE, FIDUCIAL_SIZE, fill=True, stroke=False)
    # Bottom-left
    c.rect(MARGIN, MARGIN, FIDUCIAL_SIZE, FIDUCIAL_SIZE, fill=True, stroke=False)
    # Bottom-right
    c.rect(PAGE_W - MARGIN - FIDUCIAL_SIZE, MARGIN, FIDUCIAL_SIZE, FIDUCIAL_SIZE, fill=True, stroke=False)
    c.setFillColor(colors.black)


def _draw_qr(c: canvas.Canvas, data: str, x: float, y: float, size: float = 90.0):
    code = qr.QrCodeWidget(data)
    b = code.getBounds()
    w = b[2] - b[0]
    h = b[3] - b[1]
    d = Drawing(size, size, transform=[size / w, 0, 0, size / h, 0, 0])
    d.add(code)
    renderPDF.draw(d, c, x, y)


def _bubble(c: canvas.Canvas, cx: float, cy: float, label: Optional[str] = None):
    c.setLineWidth(1)
    c.setStrokeColor(colors.black)
    c.circle(cx, cy, BUBBLE_R, stroke=1, fill=0)
    if label:
        c.setFont("Helvetica", 10)
        c.drawRightString(cx - BUBBLE_R - 6, cy - 3, label)


def generate_answer_sheet_for_student(
    db: Session,
    exam: Exam,
    student: Student,
    logo_path: Optional[str] = None,
    version: str = "V1"
) -> str:
    """
    Gera o cartão-resposta OMR nominal para o aluno.
    """
    out_dir = _exam_storage_dir(exam.id)
    out_path = os.path.join(out_dir, f"omr_exam{exam.id}_student{student.id}_{version}.pdf")

    c = canvas.Canvas(out_path, pagesize=A4)
    # Cabeçalho
    _draw_header(c, title="Cartão-Resposta", subtitle=exam.title or "", logo_path=logo_path)

    # Identificação do aluno
    c.setFont("Helvetica", 11)
    c.drawString(MARGIN, PAGE_H - MARGIN - HEADER_H + 10, f"Aluno: {student.name}  |  RA: {student.ra}  |  Turma: {student.school_class.name}")
    c.drawString(MARGIN, PAGE_H - MARGIN - HEADER_H - 6, "Imprimir em 100% (sem ajustar à página)")

    # Fiduciais
    _draw_fiducials(c)

    # QR Code (canto superior direito, abaixo do fiducial)
    qr_x = PAGE_W - MARGIN - FIDUCIAL_SIZE - 100
    qr_y = PAGE_H - MARGIN - FIDUCIAL_SIZE - 120
    qr_data = f"{exam.id}|{student.id}|{version}"
    _draw_qr(c, qr_data, qr_x, qr_y, size=90.0)

    # Grade de bolhas: posição de início
    start_x = MARGIN + 80
    start_y = PAGE_H - MARGIN - HEADER_H - 40

    # Número de questões = tamanho da seleção. Se não houver seleção explícita, cair no total de questões.
    selection = db.query(ExamQuestionLink).filter(ExamQuestionLink.exam_id == exam.id).order_by(ExamQuestionLink.order_idx.asc()).all()
    if selection:
        num_questions = len(selection)
    else:
        num_questions = db.query(Question).filter(Question.exam_id == exam.id).count()

    # Distribuição em colunas (ex.: 25 por coluna)
    per_col = 25
    cols = (num_questions + per_col - 1) // per_col

    labels = ["A", "B", "C", "D"] if exam.options_count == 4 else ["A", "B", "C", "D", "E"]

    c.setFont("Helvetica-Bold", 11)
    c.drawString(start_x, start_y + 20, "Preencha totalmente a bolha da alternativa escolhida.")
    c.setFont("Helvetica", 10)

    for col in range(cols):
        col_x = start_x + col * (BUBBLE_SPACING_H * (len(labels) + 2))
        y = start_y - 10

        for i in range(per_col):
            qn = col * per_col + i + 1
            if qn > num_questions:
                break
            # número da questão
            c.setFont("Helvetica-Bold", 10)
            c.drawString(col_x, y, f"{qn:02d}")
            # bolhas A..(D/E)
            c.setFont("Helvetica", 10)
            bx = col_x + 30
            for lab in labels:
                _bubble(c, bx, y + 3, label=lab)
                bx += BUBBLE_SPACING_H
            y -= BUBBLE_SPACING_V

    # Rodapé
    _draw_footer(c, exam_code=f"EXAM-{exam.id}", page_num=1)
    c.save()
    return out_path


# ------------------------------------------------------------------------------
# Geração em lote
# ------------------------------------------------------------------------------
def generate_exam_pdfs_for_class(
    db: Session,
    exam: Exam,
    class_id: int,
    logo_path: Optional[str] = None,
    per_student_files: bool = True
) -> Dict[str, List[str]]:
    """
    Gera PDFs para toda a turma (class_id) do exame:
    - Se per_student_files=True, gera 1 caderno + 1 OMR por aluno (retorna lista de paths)
    - Caso queira um único PDF agregado por turma, isso pode ser implementado depois
      (concatenação com reportlab ou PyPDF2).
    """
    out = {"booklets": [], "answer_sheets": []}

    students = db.query(Student).filter(Student.class_id == class_id).order_by(Student.id).all()
    for st in students:
        p1 = generate_exam_booklet_for_student(db, exam, st, logo_path=logo_path)
        p2 = generate_answer_sheet_for_student(db, exam, st, logo_path=logo_path, version="V1")
        out["booklets"].append(p1)
        out["answer_sheets"].append(p2)

    return out


def generate_exam_pdfs_for_student(
    db: Session,
    exam: Exam,
    student_id: int,
    logo_path: Optional[str] = None
) -> Dict[str, str]:
    """
    Gera PDFs apenas para um aluno (útil para reimpressões).
    """
    st = db.get(Student, student_id)
    if not st:
        raise ValueError("Aluno não encontrado.")
    return {
        "booklet": generate_exam_booklet_for_student(db, exam, st, logo_path=logo_path),
        "answer_sheet": generate_answer_sheet_for_student(db, exam, st, logo_path=logo_path, version="V1")
    }