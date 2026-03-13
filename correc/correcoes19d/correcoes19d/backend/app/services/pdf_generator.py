# =============================================================================
# app/services/pdf_generator.py
# =============================================================================
# Passo 7:  caderno 2 colunas + folha OMR
# Passo 13: capa personalizada por aluno + página de rascunho a cada 3 páginas
#           correção do contador "Questões" no cabeçalho
# =============================================================================

from __future__ import annotations

import io
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, NextPageTemplate, PageBreak,
    PageTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether,
)
from reportlab.platypus.flowables import HRFlowable
from PIL import Image as PILImage
import qrcode
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from app.core.settings import settings

# =============================================================================
# CONSTANTES
# =============================================================================
STORAGE_BASE    = "/app/storage"
PAGE_W, PAGE_H  = A4
MARGIN_TOP      = 3.0 * cm
MARGIN_BOTTOM   = 2.0 * cm
MARGIN_INTERIOR = 3.0 * cm
MARGIN_EXTERIOR = 2.0 * cm
COL_GAP         = 0.5 * cm
USABLE_W        = PAGE_W - MARGIN_INTERIOR - MARGIN_EXTERIOR
COL_W           = (USABLE_W - COL_GAP) / 2
FOOTER_H        = 1.0 * cm
USABLE_H        = PAGE_H - MARGIN_TOP - MARGIN_BOTTOM - FOOTER_H
HEADER_H        = 4.0 * cm
_BASE_FONT      = "Times-Roman"
_BASE_FONT_BOLD = "Times-Bold"
_BASE_SIZE      = 12
_BASE_LEADING   = 18

# =============================================================================
# ESTILOS
# =============================================================================
def _make_styles():
    s = {}
    s["body"] = ParagraphStyle("body", fontName=_BASE_FONT, fontSize=_BASE_SIZE, leading=_BASE_LEADING, alignment=TA_JUSTIFY, spaceAfter=6)
    s["stem"] = ParagraphStyle("stem", fontName=_BASE_FONT, fontSize=_BASE_SIZE, leading=_BASE_LEADING, alignment=TA_JUSTIFY, spaceBefore=4, spaceAfter=4)
    s["option"] = ParagraphStyle("option", fontName=_BASE_FONT, fontSize=_BASE_SIZE, leading=_BASE_LEADING, alignment=TA_JUSTIFY, leftIndent=12, spaceAfter=2)
    s["question_number"] = ParagraphStyle("question_number", fontName=_BASE_FONT_BOLD, fontSize=_BASE_SIZE, leading=_BASE_LEADING, spaceBefore=8, spaceAfter=2)
    s["header_title"] = ParagraphStyle("header_title", fontName=_BASE_FONT_BOLD, fontSize=14, leading=21, alignment=TA_CENTER, spaceAfter=4)
    s["footer"] = ParagraphStyle("footer", fontName=_BASE_FONT, fontSize=10, leading=12, alignment=TA_CENTER)
    s["instruction"] = ParagraphStyle("instruction", fontName="Times-Italic", fontSize=_BASE_SIZE, leading=_BASE_LEADING, alignment=TA_JUSTIFY, spaceAfter=6)
    return s

STYLES = _make_styles()

# =============================================================================
# LATEX
# =============================================================================
def _render_latex_to_image(expr, fontsize=12):
    try:
        fig, ax = plt.subplots(figsize=(0.01, 0.01))
        ax.axis("off")
        t = ax.text(0.5, 0.5, f"${expr}$", fontsize=fontsize, ha="center", va="center", transform=fig.transFigure, family="serif")
        fig.canvas.draw()
        bbox = t.get_window_extent(renderer=fig.canvas.get_renderer())
        dpi = 150
        fig.set_size_inches(max(bbox.width/dpi+0.1, 0.5), max(bbox.height/dpi+0.1, 0.3))
        fig.canvas.draw()
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        fig.savefig(tmp.name, dpi=dpi, bbox_inches="tight", transparent=True, pad_inches=0.02)
        plt.close(fig)
        return tmp.name
    except Exception as e:
        try: plt.close("all")
        except: pass
        return None

def _parse_text_with_latex(text, style):
    parts = re.split(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)', text, flags=re.DOTALL)
    if len(parts) == 1:
        return [Paragraph(text, style)]
    flowables = []
    tmp_files = []
    for i, part in enumerate(parts):
        if not part: continue
        if i % 2 == 0:
            if part.strip(): flowables.append(Paragraph(part, style))
        else:
            p = _render_latex_to_image(part, fontsize=_BASE_SIZE)
            if p:
                tmp_files.append(p)
                try:
                    with PILImage.open(p) as img: pw, ph = img.size
                    max_w = COL_W * 0.8
                    flowables.append(Image(p, width=max_w, height=ph*(max_w/pw)))
                except: flowables.append(Paragraph(f"[{part}]", style))
            else: flowables.append(Paragraph(f"[{part}]", style))
    if not hasattr(_parse_text_with_latex, "_tmp_files"): _parse_text_with_latex._tmp_files = []
    _parse_text_with_latex._tmp_files.extend(tmp_files)
    return flowables

def _cleanup_latex_temps():
    for p in getattr(_parse_text_with_latex, "_tmp_files", []):
        try:
            if os.path.exists(p): os.unlink(p)
        except: pass
    _parse_text_with_latex._tmp_files = []

# =============================================================================
# STORAGE
# =============================================================================
def _coerce_storage_dir(raw):
    base = Path(raw or "/app/storage")
    if not base.is_absolute():
        base = Path("/app") / base
    try:
        base.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        # CI/test: sem permissão em /app — usa diretório temporário
        import tempfile
        base = Path(tempfile.gettempdir()) / "samba_storage"
        base.mkdir(parents=True, exist_ok=True)
    return base

_STORAGE_ROOT = _coerce_storage_dir(getattr(settings, "STORAGE_DIR", None))

def exam_storage_dir(exam_id, create=False):
    path = _STORAGE_ROOT / "exams" / str(exam_id)
    if create: path.mkdir(parents=True, exist_ok=True)
    return path

def _exam_storage_dir(exam_id):
    return str(exam_storage_dir(exam_id, create=True))

# =============================================================================
# CAPA
# =============================================================================
def _draw_cover(canvas, exam, student_name, student_ra, student_class, n_questions, logo_path=None):
    canvas.saveState()

    # --- Cabeçalho institucional ---
    hdr_top = PAGE_H - 1.2 * cm
    hdr_bot = PAGE_H - 4.0 * cm
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN_INTERIOR, hdr_bot, PAGE_W - MARGIN_EXTERIOR, hdr_bot)
    canvas.line(MARGIN_INTERIOR, hdr_top, PAGE_W - MARGIN_EXTERIOR, hdr_top)

    # Logo SP (assets ou logo_path externo)
    logo_x = MARGIN_INTERIOR
    logo_y = hdr_bot + 0.2 * cm
    logo_w = 2.0 * cm
    logo_h = hdr_top - hdr_bot - 0.4 * cm
    _sp_asset = os.path.join(STORAGE_BASE, "assets", "logo_sp.png")
    _sp_path  = logo_path if (logo_path and os.path.exists(logo_path)) else (_sp_asset if os.path.exists(_sp_asset) else None)
    if _sp_path:
        canvas.drawImage(_sp_path, logo_x, logo_y, width=logo_w, height=logo_h,
                         preserveAspectRatio=True, mask="auto")
    else:
        canvas.setFillColorRGB(0.75, 0.75, 0.75)
        canvas.rect(logo_x, logo_y, logo_w, logo_h, fill=1, stroke=0)
        canvas.setFillColorRGB(0, 0, 0)
        canvas.setFont("Times-Bold", 7)
        canvas.drawCentredString(logo_x + logo_w/2, logo_y + logo_h*0.55, "SÃO")
        canvas.drawCentredString(logo_x + logo_w/2, logo_y + logo_h*0.35, "PAULO")

    tx = MARGIN_INTERIOR + logo_w + 0.3 * cm
    canvas.setFillColorRGB(0, 0, 0)
    canvas.setFont("Times-Bold", 7.5)
    canvas.drawString(tx, hdr_bot + 2.3 * cm, "GOVERNO DO ESTADO DE SÃO PAULO – SECRETARIA DE ESTADO DA EDUCAÇÃO")
    canvas.setFont(_BASE_FONT, 7.5)
    canvas.drawString(tx, hdr_bot + 1.8 * cm, "UNIDADE REGIONAL DE ENSINO – REGIÃO BAURU – EE PROF. CHRISTINO CABRAL")
    canvas.drawString(tx, hdr_bot + 1.3 * cm, "Rua Gerson França, 19-165 – Jardim Estoril II – CEP: 17016-000")
    canvas.drawString(tx, hdr_bot + 0.8 * cm, "Telefones: (14) 3223-3855 (WhatsApp); (14) 3227-4664 – E-mail: e625598a@educacao.sp.gov.br")

    # Logo Ensino Integral (assets ou placeholder)
    bi_x = PAGE_W - MARGIN_EXTERIOR - 2.2 * cm
    bi_y = hdr_bot + 0.2 * cm
    bi_w = 2.0 * cm
    bi_h = hdr_top - hdr_bot - 0.4 * cm
    _int_asset = os.path.join(STORAGE_BASE, "assets", "logo_integral.png")
    if os.path.exists(_int_asset):
        canvas.drawImage(_int_asset, bi_x, bi_y, width=bi_w, height=bi_h,
                         preserveAspectRatio=True, mask="auto")
    else:
        canvas.setFillColorRGB(0.0, 0.45, 0.7)
        canvas.roundRect(bi_x, bi_y, bi_w, bi_h, 3, fill=1, stroke=0)
        canvas.setFillColorRGB(1, 1, 1)
        canvas.setFont("Times-Bold", 7)
        canvas.drawCentredString(bi_x + bi_w/2, bi_y + bi_h*0.55, "ENSINO")
        canvas.drawCentredString(bi_x + bi_w/2, bi_y + bi_h*0.35, "INTEGRAL")

    # --- Título ---
    canvas.setFillColorRGB(0, 0, 0)
    title_y = hdr_bot - 3.5 * cm
    canvas.setFont("Times-Bold", 20)
    canvas.drawCentredString(PAGE_W / 2, title_y, (exam.title or "SIMULADO").upper())
    canvas.setLineWidth(1.5)
    canvas.line(MARGIN_INTERIOR + 2*cm, title_y - 0.5*cm, PAGE_W - MARGIN_EXTERIOR - 2*cm, title_y - 0.5*cm)

    # --- Instruções ---
    instructions = [
        "Confira seus dados impressos neste caderno. Cuidado com a folha de respostas, a mesma não será reposta.",
        "Assine com caneta de tinta preta a Folha de Respostas apenas no local indicado.",
        f"Esta prova contém {n_questions} questões objetivas.",
        "Quando for permitido abrir o caderno, verifique se está completo ou se apresenta imperfeições. Caso haja algum problema, informe ao professor.",
        "Para cada questão, o candidato deverá assinalar apenas uma alternativa na Folha de Respostas, utilizando caneta de tinta azul ou preta.",
        "Esta prova terá duração total de 2h e 30min e o candidato somente poderá sair se permitido pelo professor aplicador, após 50 min contados a partir do início da prova.",
        "Ao final da prova, entregue ao professor a folha de Respostas obrigatoriamente e o Caderno de Questões se o professor solicitar.",
    ]

    iy = title_y - 1.0 * cm
    lh = 13
    max_w_pts = USABLE_W - 0.6 * cm

    for instr in instructions:
        canvas.setFont("Times-Bold", 9.5)
        canvas.drawString(MARGIN_INTERIOR, iy, "►")
        canvas.setFont(_BASE_FONT, 9.5)
        words = instr.split()
        lines, cur = [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if canvas.stringWidth(test, _BASE_FONT, 9.5) < max_w_pts:
                cur = test
            else:
                lines.append(cur); cur = w
        if cur: lines.append(cur)
        for li, line in enumerate(lines):
            canvas.drawString(MARGIN_INTERIOR + 0.5*cm, iy, line)
            iy -= lh
        iy -= 4

    # --- Campos do aluno (caixas rounded) ---
    box_h  = 0.7 * cm
    box_r  = 4        # raio do arredondamento
    pad_x  = 0.25 * cm
    fill_c = (0.96, 0.96, 0.96)  # cinza bem claro

    def _box(lbl, value, bx, by, bw):
        """Desenha label + caixa rounded com valor preenchido."""
        canvas.setFont("Times-Bold", 11)
        canvas.setFillColorRGB(0, 0, 0)
        canvas.drawString(bx, by + box_h * 0.28, lbl)
        lbl_w = canvas.stringWidth(lbl, "Times-Bold", 11) + pad_x
        # caixa
        canvas.setFillColorRGB(*fill_c)
        canvas.setStrokeColorRGB(0.4, 0.4, 0.4)
        canvas.setLineWidth(0.5)
        canvas.roundRect(bx + lbl_w, by, bw - lbl_w, box_h, box_r, fill=1, stroke=1)
        # valor dentro da caixa
        if value:
            canvas.setFillColorRGB(0, 0, 0)
            canvas.setFont(_BASE_FONT, 10.5)
            canvas.drawString(bx + lbl_w + pad_x, by + box_h * 0.28, str(value))

    fy = 8.5 * cm
    full_w = PAGE_W - MARGIN_INTERIOR - MARGIN_EXTERIOR

    # Linha 1: Nome (largura total)
    _box("Nome:", student_name, MARGIN_INTERIOR, fy, full_w)

    # Linha 2: RA / Série / Data
    ry = fy - 1.1 * cm
    ra_w    = full_w * 0.38
    serie_w = full_w * 0.25
    data_w  = full_w * 0.37
    _box("R.A:",   student_ra,    MARGIN_INTERIOR,                      ry, ra_w)
    _box("Série:", student_class, MARGIN_INTERIOR + ra_w + 0.2*cm,      ry, serie_w)
    _box("Data:",  datetime.now().strftime("%d/%m/%Y"),
                                  MARGIN_INTERIOR + ra_w + serie_w + 0.4*cm, ry, data_w)


    # --- Rodapé da capa ---
    canvas.setLineWidth(0.4)
    canvas.line(MARGIN_INTERIOR, MARGIN_BOTTOM, PAGE_W - MARGIN_EXTERIOR, MARGIN_BOTTOM)
    canvas.setFont("Times-Italic", 9)
    canvas.drawString(MARGIN_INTERIOR, MARGIN_BOTTOM - 0.45*cm, "Confidencial até momento da aplicação.")

    canvas.restoreState()

# =============================================================================
# CALLBACKS DE PÁGINA
# =============================================================================
def _draw_questions_header(canvas, doc, exam, n_questions):
    canvas.saveState()
    ty = PAGE_H - MARGIN_TOP
    canvas.setFont(_BASE_FONT_BOLD, 11)
    canvas.drawString(MARGIN_INTERIOR, ty - 0.7*cm, exam.title or "SIMULADO")
    canvas.setFont(_BASE_FONT, 10)
    if exam.area:
        canvas.drawString(MARGIN_INTERIOR, ty - 1.3*cm, f"Área: {exam.area}")
    canvas.drawRightString(PAGE_W - MARGIN_EXTERIOR, ty - 0.7*cm, f"Data: {datetime.now().strftime('%d/%m/%Y')}")
    canvas.drawRightString(PAGE_W - MARGIN_EXTERIOR, ty - 1.3*cm, f"Questões: {n_questions}")
    canvas.setLineWidth(0.6)
    canvas.line(MARGIN_INTERIOR, ty - HEADER_H + 0.3*cm, PAGE_W - MARGIN_EXTERIOR, ty - HEADER_H + 0.3*cm)
    canvas.restoreState()

def _draw_footer(canvas, doc):
    canvas.saveState()
    fy = MARGIN_BOTTOM - 0.3*cm
    canvas.setLineWidth(0.4)
    canvas.line(MARGIN_INTERIOR, fy + 0.5*cm, PAGE_W - MARGIN_EXTERIOR, fy + 0.5*cm)
    canvas.setFont(_BASE_FONT, 10)
    canvas.drawCentredString(PAGE_W/2, fy, str(canvas.getPageNumber()))
    canvas.restoreState()

def _draw_draft_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Bold", 90)
    canvas.setFillColorRGB(0.88, 0.88, 0.88)
    canvas.translate(PAGE_W/2, PAGE_H/2)
    canvas.rotate(45)
    canvas.drawCentredString(0, 0, "RASCUNHO")
    canvas.restoreState()
    _draw_footer(canvas, doc)

# =============================================================================
# BUILD BOOKLET
# =============================================================================
def _build_booklet(exam, questions, output_path, student_name="", student_id=0,
                   student_ra="", student_class="", logo_path=None):
    n_questions = len(questions)

    doc = BaseDocTemplate(
        output_path, pagesize=A4,
        leftMargin=MARGIN_INTERIOR, rightMargin=MARGIN_EXTERIOR,
        topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM,
        title=exam.title or "Simulado", author="SAMBA Simulator",
    )

    def frames_odd(hs=0.0):
        ch = PAGE_H - MARGIN_TOP - hs - MARGIN_BOTTOM - FOOTER_H
        return [
            Frame(MARGIN_INTERIOR, MARGIN_BOTTOM+FOOTER_H, COL_W, ch, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="o1"),
            Frame(MARGIN_INTERIOR+COL_W+COL_GAP, MARGIN_BOTTOM+FOOTER_H, COL_W, ch, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="o2"),
        ]

    def frames_even(hs=0.0):
        ch = PAGE_H - MARGIN_TOP - hs - MARGIN_BOTTOM - FOOTER_H
        return [
            Frame(MARGIN_EXTERIOR, MARGIN_BOTTOM+FOOTER_H, COL_W, ch, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="e1"),
            Frame(MARGIN_EXTERIOR+COL_W+COL_GAP, MARGIN_BOTTOM+FOOTER_H, COL_W, ch, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="e2"),
        ]

    full_frame = Frame(0, 0, PAGE_W, PAGE_H, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="full")
    def _on_question_page(canvas, doc):
        _draw_footer(canvas, doc)

    def _on_draft_page(canvas, doc):
        _draw_draft_page(canvas, doc)

    # Captura variáveis no closure para os callbacks onPage
    _exam = exam
    _sn   = student_name
    _sr   = student_ra
    _sc   = student_class
    _n    = n_questions
    _lp   = logo_path

    cover_tpl   = PageTemplate(id="cover",   frames=[full_frame],
                               onPage=lambda c,d: _draw_cover(c, _exam, _sn, _sr, _sc, _n, _lp))
    first_q_tpl = PageTemplate(id="first_q", frames=frames_odd(HEADER_H),
                               onPage=lambda c,d: (_draw_questions_header(c,d,_exam,_n), _on_question_page(c,d)))
    odd_tpl     = PageTemplate(id="odd",     frames=frames_odd(),  onPage=_on_question_page)
    even_tpl    = PageTemplate(id="even",    frames=frames_even(), onPage=_on_question_page)
    draft_tpl   = PageTemplate(id="draft",   frames=[full_frame],  onPage=_on_draft_page)

    doc.addPageTemplates([cover_tpl, first_q_tpl, odd_tpl, even_tpl, draft_tpl])

    story = []

    # CAPA (pg 1) — template "cover" é o primeiro da lista
    story.append(Spacer(1, 0.1))

    # Primeira página de questões
    story.append(NextPageTemplate("first_q"))
    story.append(PageBreak())

    story.append(Paragraph(
        "Leia atentamente cada questão antes de responder. "
        "Marque apenas uma alternativa por questão na folha de respostas. "
        "Não é permitido o uso de corretivo ou caneta diferente da azul/preta.",
        STYLES["instruction"],
    ))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=0.4, color=colors.black))
    story.append(Spacer(1, 0.2*cm))
    story.append(NextPageTemplate("odd"))

    # Questões — rascunho inserido explicitamente a cada DRAFT_EVERY questões
    DRAFT_EVERY = 6  # insere rascunho após cada grupo de 6 questões
    for qi, q in enumerate(questions):
        # Insere rascunho antes da questão que inicia novo grupo (exceto o primeiro)
        if qi > 0 and qi % DRAFT_EVERY == 0:
            story.append(NextPageTemplate("draft"))
            story.append(PageBreak())
            story.append(Spacer(1, 0.1))  # conteúdo vazio na página de rascunho
            story.append(NextPageTemplate("odd"))
            story.append(PageBreak())

        block = []
        block.append(Paragraph(f"<b>Questão {q.get('number', qi+1)}</b>", STYLES["question_number"]))

        img_path = q.get("image")
        if img_path and os.path.exists(img_path):
            try:
                with PILImage.open(img_path) as pi: iw, ih = pi.size
                max_w = COL_W * 0.9
                scale = min(max_w/iw, (USABLE_H*0.3)/ih)
                block.append(Image(img_path, width=iw*scale, height=ih*scale))
                block.append(Spacer(1, 0.2*cm))
            except Exception as e:
                print(f"[pdf_generator] img error: {e}")

        block.extend(_parse_text_with_latex(q.get("stem",""), STYLES["stem"]))
        block.append(Spacer(1, 0.15*cm))

        for opt in q.get("options", []):
            block.extend(_parse_text_with_latex(f"<b>{opt.get('label','')}</b>) {opt.get('text','')}", STYLES["option"]))

        block.append(Spacer(1, 0.3*cm))
        try: story.append(KeepTogether(block))
        except: story.extend(block)

    story.append(Spacer(1, 1*cm))
    doc.build(story)
    _cleanup_latex_temps()

# =============================================================================
# BUILD ANSWER SHEET
# =============================================================================
def _build_answer_sheet(exam, output_path, student_name="", student_id=0,
                        student_ra="", student_class="", n_questions=None):
    """
    Folha de respostas OMR com:
    - Cabeçalho idêntico ao caderno (logos + escola + dados do aluno)
    - Círculos (A)(B)(C)(D)(E) em linhas alternadas branco/cinza
    - Grid dentro de roundRect
    - Barcode automático
    - Colunas automáticas: ≤30→2col | ≤60→3col | >60→4col
    """
    from reportlab.pdfgen.canvas import Canvas as _Canvas

    if not n_questions:
        n_questions = getattr(exam, "omr_rows", 10) or 10

    OPTIONS    = ["A", "B", "C", "D", "E"]
    N_OPTS     = len(OPTIONS)

    if n_questions <= 30:
        n_grid_cols = 2
    elif n_questions <= 60:
        n_grid_cols = 3
    else:
        n_grid_cols = 4

    rows_per_col = -(-n_questions // n_grid_cols)

    c = _Canvas(output_path, pagesize=A4)
    W, H = A4
    ML = MARGIN_INTERIOR
    MR = MARGIN_EXTERIOR

    # ── Cabeçalho institucional (idêntico ao caderno) ──────────────
    hdr_top = H - 1.2 * cm
    hdr_bot = H - 4.0 * cm
    c.setLineWidth(0.5)
    c.line(ML, hdr_bot, W - MR, hdr_bot)
    c.line(ML, hdr_top, W - MR, hdr_top)

    # Logo SP
    logo_x = ML
    logo_y = hdr_bot + 0.2 * cm
    logo_w = 2.0 * cm
    logo_h = hdr_top - hdr_bot - 0.4 * cm
    _sp_asset = os.path.join(STORAGE_BASE, "assets", "logo_sp.png")
    if os.path.exists(_sp_asset):
        c.drawImage(_sp_asset, logo_x, logo_y, width=logo_w, height=logo_h,
                    preserveAspectRatio=True, mask="auto")
    else:
        c.setFillColorRGB(0.75, 0.75, 0.75)
        c.rect(logo_x, logo_y, logo_w, logo_h, fill=1, stroke=0)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Times-Bold", 7)
        c.drawCentredString(logo_x + logo_w/2, logo_y + logo_h*0.55, "SÃO")
        c.drawCentredString(logo_x + logo_w/2, logo_y + logo_h*0.35, "PAULO")

    tx = ML + logo_w + 0.3 * cm
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Times-Bold", 7.5)
    c.drawString(tx, hdr_bot + 2.3 * cm, "GOVERNO DO ESTADO DE SÃO PAULO – SECRETARIA DE ESTADO DA EDUCAÇÃO")
    c.setFont(_BASE_FONT, 7.5)
    c.drawString(tx, hdr_bot + 1.8 * cm, "UNIDADE REGIONAL DE ENSINO – REGIÃO BAURU – EE PROF. CHRISTINO CABRAL")
    c.drawString(tx, hdr_bot + 1.3 * cm, "Rua Gerson França, 19-165 – Jardim Estoril II – CEP: 17016-000")
    c.drawString(tx, hdr_bot + 0.8 * cm, "Telefones: (14) 3223-3855 (WhatsApp); (14) 3227-4664")

    # Logo Integral
    bi_x = W - MR - 2.2 * cm
    bi_y = hdr_bot + 0.2 * cm
    bi_w = 2.0 * cm
    bi_h = logo_h
    _int_asset = os.path.join(STORAGE_BASE, "assets", "logo_integral.png")
    if os.path.exists(_int_asset):
        c.drawImage(_int_asset, bi_x, bi_y, width=bi_w, height=bi_h,
                    preserveAspectRatio=True, mask="auto")
    else:
        c.setFillColorRGB(0.0, 0.45, 0.7)
        c.roundRect(bi_x, bi_y, bi_w, bi_h, 3, fill=1, stroke=0)
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Times-Bold", 7)
        c.drawCentredString(bi_x + bi_w/2, bi_y + bi_h*0.55, "ENSINO")
        c.drawCentredString(bi_x + bi_w/2, bi_y + bi_h*0.35, "INTEGRAL")

    # ── Título da folha ────────────────────────────────────────────
    y = hdr_bot - 0.7 * cm
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Times-Bold", 13)
    c.drawCentredString(W/2, y, "FOLHA DE RESPOSTAS")
    c.setFont(_BASE_FONT, 9)
    c.drawCentredString(W/2, y - 0.4 * cm, (exam.title or "SIMULADO").upper())

    # ── Campos do aluno (caixas rounded — igual capa) ──────────────
    y -= 1.1 * cm
    from datetime import datetime as _dt
    today = _dt.now().strftime("%d/%m/%Y")

    BOX_H = 0.55 * cm
    BOX_R = 3       # raio rounded

    def _field_box(label, value, bx, by, bw):
        c.setStrokeColorRGB(0.3, 0.3, 0.3)
        c.setFillColorRGB(1, 1, 1)
        c.setLineWidth(0.5)
        c.roundRect(bx, by - BOX_H, bw, BOX_H, BOX_R, fill=1, stroke=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Times-Bold", 7.5)
        c.drawString(bx + 0.15 * cm, by - BOX_H * 0.45, f"{label}  ")
        c.setFont(_BASE_FONT, 8)
        lw = c.stringWidth(label + "  ", "Times-Bold", 7.5)
        c.drawString(bx + 0.15 * cm + lw, by - BOX_H * 0.45, value)

    USABLE_W_omr = W - ML - MR

    # Linha 1: Nome (largura total)
    _field_box("Nome:", student_name or "", ML, y, USABLE_W_omr)
    y -= BOX_H + 0.2 * cm

    # Linha 2: RA | Série | Data
    fw = USABLE_W_omr / 3 - 0.1 * cm
    _field_box("R.A:",   student_ra    or "", ML,                    y, fw)
    _field_box("Série:", student_class or "", ML + fw + 0.15 * cm,  y, fw)
    _field_box("Data:",  today,               ML + 2*(fw + 0.15*cm), y, fw)
    y -= BOX_H + 0.5 * cm

    # ── Instruções ─────────────────────────────────────────────────
    c.setFont(_BASE_FONT, 7.5)
    instructions = [
        "■  Marque apenas UMA alternativa por questão com caneta azul ou preta.",
        "■  Preencha completamente o círculo.  Marcações rasuradas anulam a questão.",
        "■  Não amasse, rasgue ou escreva fora dos lugares indicados.",
    ]
    for inst in instructions:
        c.setFillColorRGB(0, 0, 0)
        c.drawString(ML, y, inst)
        y -= 0.38 * cm
    y -= 0.3 * cm

    # ── Grid de questões dentro de roundRect ───────────────────────
    CIRCLE_R  = 0.21 * cm
    ROW_H     = 0.62 * cm
    NUM_W     = 0.75 * cm
    OPT_W     = 0.88 * cm
    COL_W_g   = NUM_W + N_OPTS * OPT_W + 0.5 * cm
    GAP       = (USABLE_W_omr - n_grid_cols * COL_W_g) / (n_grid_cols + 1)

    grid_h    = rows_per_col * ROW_H + ROW_H  # altura total do grid + header
    grid_top  = y
    grid_bot  = grid_top - grid_h

    # Fundo rounded do grid
    GRID_PAD = 0.25 * cm
    c.setFillColorRGB(0.97, 0.97, 0.97)
    c.setStrokeColorRGB(0.5, 0.5, 0.5)
    c.setLineWidth(0.6)
    c.roundRect(ML - GRID_PAD, grid_bot - GRID_PAD,
                USABLE_W_omr + 2*GRID_PAD, grid_h + 2*GRID_PAD,
                6, fill=1, stroke=1)
    c.setFillColorRGB(0, 0, 0)

    # Cabeçalho do grid (Nº A B C D E)
    y_hdr = grid_top - ROW_H * 0.3
    for gc in range(n_grid_cols):
        col_x = ML + GAP + gc * (COL_W_g + GAP)
        c.setFont("Times-Bold", 8)
        c.setFillColorRGB(0, 0, 0)
        c.drawCentredString(col_x + NUM_W/2, y_hdr, "Nº")
        for oi, opt in enumerate(OPTIONS):
            c.drawCentredString(col_x + NUM_W + (oi + 0.5) * OPT_W, y_hdr, opt)

    # Linhas de questão
    q_num = 1
    for row in range(rows_per_col):
        row_y    = grid_top - (row + 1) * ROW_H
        row_mid  = row_y + ROW_H * 0.52

        # Fundo alternado dentro do roundRect
        if row % 2 == 0:
            c.setFillColorRGB(1, 1, 1)
        else:
            c.setFillColorRGB(0.91, 0.91, 0.91)

        for gc in range(n_grid_cols):
            if q_num + gc * rows_per_col > n_questions and gc > 0:
                continue
            col_x = ML + GAP + gc * (COL_W_g + GAP)
            # faixa de fundo para esta célula
            c.rect(col_x - GAP/2, row_y, COL_W_g + GAP/2, ROW_H, fill=1, stroke=0)

        c.setFillColorRGB(0, 0, 0)

        for gc in range(n_grid_cols):
            q = row + gc * rows_per_col + 1
            if q > n_questions:
                break
            col_x = ML + GAP + gc * (COL_W_g + GAP)

            # Número
            c.setFont("Times-Bold", 8)
            c.drawRightString(col_x + NUM_W - 0.1 * cm, row_mid - 0.1*cm, f"{q:02d}")

            # Círculos
            for oi in range(N_OPTS):
                cx = col_x + NUM_W + (oi + 0.5) * OPT_W
                c.setLineWidth(0.7)
                c.setStrokeColorRGB(0.2, 0.2, 0.2)
                c.setFillColorRGB(1, 1, 1)
                c.circle(cx, row_mid, CIRCLE_R, fill=1, stroke=1)
                c.setFillColorRGB(0.2, 0.2, 0.2)
                c.setFont(_BASE_FONT, 6)
                c.drawCentredString(cx, row_mid - CIRCLE_R * 0.5, OPTIONS[oi])

        q_num += 1

    # ── Barcode ────────────────────────────────────────────────────
    bar_y = grid_bot - GRID_PAD - 1.5 * cm
    try:
        from reportlab.graphics.barcode import code128
        bc = code128.Code128(
            f"SAMBA-E{exam.id}-S{student_id}",
            barHeight=0.9 * cm, barWidth=0.018 * cm,
            humanReadable=True, fontSize=6,
        )
        bc.drawOn(c, W/2 - bc.width/2, bar_y)
    except Exception as e:
        c.setFont(_BASE_FONT, 7)
        c.setFillColorRGB(0, 0, 0)
        c.drawCentredString(W/2, bar_y + 0.3 * cm, f"SAMBA-E{exam.id}-S{student_id}")

    c.setFont(_BASE_FONT, 6.5)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawCentredString(W/2, bar_y - 0.4 * cm, "Sistema de Avaliação SAMBA — Folha de Respostas")

    c.save()

# =============================================================================
# FUNÇÕES PÚBLICAS
# =============================================================================
def _questions_from_exam(db, exam, class_id=None):
    from app.models.exam import ExamQuestionLink, QuestionImage
    links = db.query(ExamQuestionLink).filter(ExamQuestionLink.exam_id==exam.id).order_by(ExamQuestionLink.order_idx).all()
    result = []
    seq = 0
    for link in links:
        q = link.question
        if not q: continue
        # Filtrar por turma quando informado
        if class_id is not None and q.class_id != class_id:
            continue
        seq += 1
        # Busca imagens do enunciado (context='stem') ordenadas por order_idx
        stem_imgs = (
            db.query(QuestionImage)
            .filter_by(question_id=q.id, context="stem")
            .order_by(QuestionImage.order_idx)
            .all()
        )
        # Caminho absoluto da primeira imagem do stem (se existir)
        image_path = None
        if stem_imgs:
            p = os.path.join(STORAGE_BASE, stem_imgs[0].storage_path)
            if os.path.exists(p):
                image_path = p
        result.append({
            "number": seq,
            "stem": q.stem,
            "options": [{"label": o.label, "text": o.text} for o in sorted(q.options, key=lambda o: o.label)],
            "image": image_path,
        })
    return result

def generate_exam_pdfs_for_student(db, exam, student_id, logo_path=None,
                                   student_name="", student_ra="", student_class="",
                                   class_id=None):
    out_dir = exam_storage_dir(exam.id, create=True)
    booklet_path = str(out_dir / f"booklet_exam{exam.id}_student{student_id}.pdf")
    omr_path     = str(out_dir / f"omr_exam{exam.id}_student{student_id}_V1.pdf")
    questions    = _questions_from_exam(db, exam, class_id=class_id)
    n_q          = len(questions)
    _build_booklet(exam=exam, questions=questions, output_path=booklet_path,
                   student_name=student_name, student_id=student_id,
                   student_ra=student_ra, student_class=student_class, logo_path=logo_path)
    _build_answer_sheet(exam=exam, output_path=omr_path, student_name=student_name,
                        student_id=student_id, student_ra=student_ra, student_class=student_class,
                        n_questions=n_q)
    return {"student_id": student_id, "booklet": booklet_path, "answer_sheet": omr_path,
            "questions": len(questions), "generated": True}

def generate_exam_pdfs_for_class(db, exam, class_id, logo_path=None):
    from app.models.school import Student
    students = db.query(Student).filter(Student.class_id==class_id).order_by(Student.name).all()
    results  = []
    for student in students:
        ra         = str(getattr(student, "ra", "") or getattr(student, "number", "") or "")
        class_name = ""
        if hasattr(student, "school_class") and student.school_class:
            class_name = student.school_class.name or ""
        results.append(generate_exam_pdfs_for_student(
            db=db, exam=exam, student_id=student.id, logo_path=logo_path,
            student_name=student.name or "", student_ra=ra, student_class=class_name,
            class_id=class_id,
        ))
    return {"class_id": class_id, "students_count": len(students), "results": results, "generated": True}

# =============================================================================
# BATCH — merge de PDFs e geração de ZIP por turma
# =============================================================================

def merge_pdfs(pdf_paths: list, output_path: str) -> str:
    """Concatena uma lista de PDFs em um único arquivo."""
    from pypdf import PdfWriter
    writer = PdfWriter()
    for p in pdf_paths:
        if os.path.exists(p):
            writer.append(p)
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path


def generate_batch_for_class(db, exam, class_id, batch_type: str) -> str:
    """
    Gera lote de PDFs para uma turma.

    batch_type:
      "booklets"   → PDF único com todos os cadernos concatenados
      "omr"        → PDF único com todas as folhas OMR concatenadas
      "individual" → ZIP com um PDF por aluno (nomeado pelo RA)

    Reutiliza PDFs já gerados — só regenera se o arquivo não existir.
    Retorna o caminho do arquivo final (PDF ou ZIP).
    """
    import zipfile
    from app.models.school import Student, SchoolClass

    cls = db.get(SchoolClass, class_id)
    class_name = (cls.name or str(class_id)).replace(" ", "").replace("/", "-") if cls else str(class_id)

    students = db.query(Student).filter(Student.class_id == class_id).order_by(Student.name).all()
    out_dir  = exam_storage_dir(exam.id, create=True)

    # Garante que todos os PDFs individuais existem
    for student in students:
        booklet_path = str(out_dir / f"booklet_exam{exam.id}_student{student.id}.pdf")
        omr_path     = str(out_dir / f"omr_exam{exam.id}_student{student.id}_V1.pdf")
        needs_regen  = (
            (batch_type in ("booklets", "individual") and not os.path.exists(booklet_path)) or
            (batch_type == "omr"                       and not os.path.exists(omr_path))
        )
        if needs_regen:
            ra         = str(getattr(student, "ra", "") or getattr(student, "number", "") or "")
            class_label = student.school_class.name if (hasattr(student, "school_class") and student.school_class) else ""
            generate_exam_pdfs_for_student(
                db=db, exam=exam, student_id=student.id,
                student_name=student.name or "", student_ra=ra, student_class=class_label,
                class_id=class_id,
            )

    if batch_type == "booklets":
        paths  = [str(out_dir / f"booklet_exam{exam.id}_student{s.id}.pdf") for s in students]
        output = str(out_dir / f"batch_{class_name}_cadernos.pdf")
        merge_pdfs(paths, output)
        return output

    elif batch_type == "omr":
        paths  = [str(out_dir / f"omr_exam{exam.id}_student{s.id}_V1.pdf") for s in students]
        output = str(out_dir / f"batch_{class_name}_omr.pdf")
        merge_pdfs(paths, output)
        return output

    elif batch_type == "individual":
        zip_path = str(out_dir / f"batch_{class_name}_individual.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for student in students:
                ra = str(getattr(student, "ra", "") or getattr(student, "number", "") or str(student.id))
                booklet_path = str(out_dir / f"booklet_exam{exam.id}_student{student.id}.pdf")
                if os.path.exists(booklet_path):
                    zf.write(booklet_path, arcname=f"{ra}_caderno.pdf")
        return zip_path

    else:
        raise ValueError(f"batch_type inválido: {batch_type}")
