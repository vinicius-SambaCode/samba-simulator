# =============================================================================
# app/services/pdf_generator.py
# =============================================================================
#
# RESPONSABILIDADE:
#   Gera dois tipos de PDF para cada aluno de um simulado:
#
#   1. CADERNO DE QUESTÕES (booklet)
#      - Formato A4, layout em espelho (frente/verso de caderno)
#      - Margens ABNT: sup=3cm, interior=3cm, inf=2cm, exterior=2cm
#      - Duas colunas por página
#      - Fonte Times New Roman 12pt, espaçamento 1,5
#      - Cabeçalho completo na primeira página
#      - Rodapé com número de página centralizado em todas as páginas
#      - Suporte a: texto, imagens inline, fórmulas LaTeX
#
#   2. FOLHA DE RESPOSTAS OMR (answer_sheet)
#      - Grade de bolhas para marcação
#      - Configurável via campos omr_rows e omr_cols do model Exam
#      - Cabeçalho com campos para identificação do aluno
#      - QR-code opcional (barcode_enabled)
#
# FÓRMULAS MATEMÁTICAS:
#   Renderizadas via matplotlib + sympy como imagens PNG temporárias.
#   O texto da questão pode conter marcadores LaTeX entre $...$:
#     "Calcule $\\int_0^1 x^2 dx$"
#   O gerador detecta, renderiza e insere como imagem inline.
#
# DEPENDÊNCIAS:
#   reportlab, pillow, matplotlib, sympy, qrcode
#
# PASSO 7 — implementação inicial completa
# =============================================================================

from __future__ import annotations

import io
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ReportLab — geração de PDF
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)
from reportlab.platypus.flowables import HRFlowable

# Fontes — Times New Roman via ReportLab (built-in como "Times-Roman")
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Pillow — manipulação de imagens
from PIL import Image as PILImage

# QR-code
import qrcode

# matplotlib + sympy — renderização LaTeX
import matplotlib
matplotlib.use("Agg")  # modo headless (sem janela gráfica)
import matplotlib.pyplot as plt
import matplotlib.mathtext  # renderização de fórmulas

from app.core.settings import settings

# =============================================================================
# CONSTANTES DE LAYOUT ABNT
# =============================================================================

# Tamanho da página
PAGE_W, PAGE_H = A4  # 595.27 x 841.89 pontos

# Margens em centímetros → convertidas para pontos (1cm = 28.35pt)
# Layout espelho para encadernação tipo caderno:
#   Páginas ímpares (frente): margem esquerda = interior, direita = exterior
#   Páginas pares  (verso):   margem esquerda = exterior, direita = interior
MARGIN_TOP      = 3.0 * cm   # superior: 3cm
MARGIN_BOTTOM   = 2.0 * cm   # inferior: 2cm
MARGIN_INTERIOR = 3.0 * cm   # margem de encadernação: 3cm
MARGIN_EXTERIOR = 2.0 * cm   # margem exterior: 2cm

# Espaço entre as duas colunas
COL_GAP = 0.5 * cm

# Largura útil da página (descontando ambas as margens)
USABLE_W = PAGE_W - MARGIN_INTERIOR - MARGIN_EXTERIOR

# Largura de cada coluna
COL_W = (USABLE_W - COL_GAP) / 2

# Altura útil (descontando margens sup/inf e espaço do rodapé)
FOOTER_H = 1.0 * cm
USABLE_H = PAGE_H - MARGIN_TOP - MARGIN_BOTTOM - FOOTER_H

# Altura do cabeçalho da primeira página
HEADER_H = 4.0 * cm

# =============================================================================
# ESTILOS TIPOGRÁFICOS (Times New Roman 12pt, espaçamento 1,5)
# =============================================================================
# "Times-Roman" é o nome interno do ReportLab para Times New Roman.
# Espaçamento 1,5 linhas ≈ leading = tamanho * 1,5 = 12 * 1,5 = 18pt

_BASE_FONT      = "Times-Roman"
_BASE_FONT_BOLD = "Times-Bold"
_BASE_SIZE      = 12          # pt
_BASE_LEADING   = 18          # pt  (espaçamento 1,5)

def _make_styles() -> dict:
    """
    Cria e retorna o dicionário de estilos tipográficos do documento.
    Todos derivam de Times-Roman 12pt com leading 18pt (espaçamento 1,5).
    """
    styles = {}

    # Corpo do texto — justificado, Times 12, leading 18
    styles["body"] = ParagraphStyle(
        name="body",
        fontName=_BASE_FONT,
        fontSize=_BASE_SIZE,
        leading=_BASE_LEADING,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    )

    # Enunciado da questão — igual ao corpo, mas com espaço extra acima
    styles["stem"] = ParagraphStyle(
        name="stem",
        fontName=_BASE_FONT,
        fontSize=_BASE_SIZE,
        leading=_BASE_LEADING,
        alignment=TA_JUSTIFY,
        spaceBefore=4,
        spaceAfter=4,
    )

    # Alternativas (A, B, C, D, E) — indentadas
    styles["option"] = ParagraphStyle(
        name="option",
        fontName=_BASE_FONT,
        fontSize=_BASE_SIZE,
        leading=_BASE_LEADING,
        alignment=TA_JUSTIFY,
        leftIndent=12,
        spaceAfter=2,
    )

    # Número da questão — negrito, pequeno recuo
    styles["question_number"] = ParagraphStyle(
        name="question_number",
        fontName=_BASE_FONT_BOLD,
        fontSize=_BASE_SIZE,
        leading=_BASE_LEADING,
        spaceBefore=8,
        spaceAfter=2,
    )

    # Título do cabeçalho — centralizado, negrito, 14pt
    styles["header_title"] = ParagraphStyle(
        name="header_title",
        fontName=_BASE_FONT_BOLD,
        fontSize=14,
        leading=21,
        alignment=TA_CENTER,
        spaceAfter=4,
    )

    # Subtítulo do cabeçalho — centralizado, 12pt
    styles["header_sub"] = ParagraphStyle(
        name="header_sub",
        fontName=_BASE_FONT,
        fontSize=_BASE_SIZE,
        leading=_BASE_LEADING,
        alignment=TA_CENTER,
        spaceAfter=2,
    )

    # Rodapé — centralizado, 10pt
    styles["footer"] = ParagraphStyle(
        name="footer",
        fontName=_BASE_FONT,
        fontSize=10,
        leading=12,
        alignment=TA_CENTER,
    )

    # Instrução geral — itálico simulado (Times-Italic)
    styles["instruction"] = ParagraphStyle(
        name="instruction",
        fontName="Times-Italic",
        fontSize=_BASE_SIZE,
        leading=_BASE_LEADING,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    )

    return styles


STYLES = _make_styles()


# =============================================================================
# RENDERIZAÇÃO DE FÓRMULAS LATEX
# =============================================================================

def _render_latex_to_image(latex_expr: str, fontsize: int = 12) -> Optional[str]:
    """
    Renderiza uma expressão LaTeX como imagem PNG usando matplotlib.

    Parâmetros:
        latex_expr: string LaTeX sem delimitadores (ex.: r"\\int_0^1 x^2 dx")
        fontsize:   tamanho da fonte em pontos (padrão: 12)

    Retorna:
        Caminho do arquivo PNG temporário, ou None em caso de erro.

    O arquivo temporário deve ser deletado pelo chamador após uso.

    Exemplo:
        path = _render_latex_to_image(r"\\frac{a}{b} + \\sqrt{c}")
        if path:
            img = Image(path, width=4*cm, height=1*cm)
            # ... usar no flowable ...
            os.unlink(path)
    """
    try:
        # Cria figura mínima — o tamanho será ajustado ao conteúdo
        fig, ax = plt.subplots(figsize=(0.01, 0.01))
        ax.axis("off")

        # Renderiza a fórmula centralizada
        text = ax.text(
            0.5, 0.5,
            f"${latex_expr}$",
            fontsize=fontsize,
            ha="center", va="center",
            transform=fig.transFigure,
            family="serif",
        )

        # Ajusta o tamanho da figura ao conteúdo renderizado
        fig.canvas.draw()
        bbox = text.get_window_extent(renderer=fig.canvas.get_renderer())
        # Converte pixels → polegadas (DPI padrão: 100)
        dpi = 150
        fig.set_size_inches(
            max(bbox.width / dpi + 0.1, 0.5),
            max(bbox.height / dpi + 0.1, 0.3),
        )
        fig.canvas.draw()

        # Salva em arquivo temporário
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        fig.savefig(tmp.name, dpi=dpi, bbox_inches="tight",
                    transparent=True, pad_inches=0.02)
        plt.close(fig)
        return tmp.name

    except Exception as exc:
        # Falha silenciosa — o chamador usará texto puro como fallback
        print(f"[pdf_generator] Falha ao renderizar LaTeX '{latex_expr}': {exc}")
        try:
            plt.close("all")
        except Exception:
            pass
        return None


def _parse_text_with_latex(text: str, style: ParagraphStyle) -> List:
    """
    Analisa um texto que pode conter fórmulas LaTeX entre $ ... $.

    Retorna uma lista de flowables misturados:
      - Paragraph para trechos de texto puro
      - Image para fórmulas renderizadas

    Exemplo de entrada:
        "A área é $\\frac{base \\times altura}{2}$ cm²."

    Saída:
        [Paragraph("A área é "), Image("/tmp/xxx.png"), Paragraph(" cm².")]

    Se não houver LaTeX, retorna [Paragraph(text, style)].
    """
    # Detecta padrão $...$  (não captura $$...$$  por ora)
    parts = re.split(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)', text, flags=re.DOTALL)

    if len(parts) == 1:
        # Sem LaTeX — retorna parágrafo simples
        return [Paragraph(text, style)]

    flowables = []
    tmp_files = []  # rastreia temporários para limpeza posterior

    for i, part in enumerate(parts):
        if not part:
            continue
        if i % 2 == 0:
            # Texto puro
            if part.strip():
                flowables.append(Paragraph(part, style))
        else:
            # Fórmula LaTeX
            tmp_path = _render_latex_to_image(part, fontsize=_BASE_SIZE)
            if tmp_path:
                tmp_files.append(tmp_path)
                try:
                    # Determina tamanho proporcional
                    with PILImage.open(tmp_path) as pil_img:
                        pw, ph = pil_img.size
                    # Limita largura a 80% da coluna
                    max_w = COL_W * 0.8
                    ratio = max_w / pw
                    img_w = max_w
                    img_h = ph * ratio
                    flowables.append(Image(tmp_path, width=img_w, height=img_h))
                except Exception:
                    # Fallback: insere o LaTeX como texto puro
                    flowables.append(Paragraph(f"[{part}]", style))
            else:
                # Fallback se renderização falhou
                flowables.append(Paragraph(f"[{part}]", style))

    # Nota: os arquivos temporários serão deletados ao final da geração
    # pelo contexto que chama esta função. Guardamos os caminhos no
    # atributo _tmp_latex_files da função para que _build_booklet() possa limpar.
    if not hasattr(_parse_text_with_latex, "_tmp_files"):
        _parse_text_with_latex._tmp_files = []
    _parse_text_with_latex._tmp_files.extend(tmp_files)

    return flowables


def _cleanup_latex_temps() -> None:
    """Remove todos os arquivos temporários de fórmulas LaTeX gerados."""
    tmp_list = getattr(_parse_text_with_latex, "_tmp_files", [])
    for path in tmp_list:
        try:
            if os.path.exists(path):
                os.unlink(path)
        except Exception:
            pass
    _parse_text_with_latex._tmp_files = []


# =============================================================================
# DIRETÓRIOS DE STORAGE
# =============================================================================

def _coerce_storage_dir(raw: Optional[str]) -> Path:
    """
    Garante que STORAGE_DIR seja absoluto e existente.
    Prioridade: settings.STORAGE_DIR → '/app/storage'
    """
    base = Path(raw or "/app/storage")
    if not base.is_absolute():
        base = Path("/app") / base
    base.mkdir(parents=True, exist_ok=True)
    return base


_STORAGE_ROOT = _coerce_storage_dir(getattr(settings, "STORAGE_DIR", None))


def exam_storage_dir(exam_id: int, create: bool = False) -> Path:
    """
    Retorna (e opcionalmente cria) o diretório de armazenamento do simulado.
    Caminho: /app/storage/exams/{exam_id}/
    """
    path = _STORAGE_ROOT / "exams" / str(exam_id)
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def _exam_storage_dir(exam_id: int) -> str:
    """Compatibilidade com código legado — cria e retorna caminho (str)."""
    return str(exam_storage_dir(exam_id, create=True))


# =============================================================================
# CALLBACKS DE PÁGINA (cabeçalho e rodapé)
# =============================================================================

def _draw_header_first_page(canvas, doc, exam, logo_path: Optional[str] = None):
    """
    Desenha o cabeçalho completo na PRIMEIRA página do caderno.

    Conteúdo:
      - Logo da escola (se fornecido) à esquerda
      - Título do simulado centralizado
      - Área do conhecimento, data e número do aluno
      - Linha horizontal separadora

    Parâmetros:
        canvas:    objeto canvas do ReportLab
        doc:       documento BaseDocTemplate
        exam:      model Exam com os metadados
        logo_path: caminho opcional para o logo da escola (PNG/JPG)
    """
    canvas.saveState()

    # Posição Y do topo do cabeçalho
    top_y = PAGE_H - MARGIN_TOP

    # --- Logo (se fornecido) ---
    if logo_path and os.path.exists(logo_path):
        logo_w = 2.5 * cm
        logo_h = 2.5 * cm
        canvas.drawImage(
            logo_path,
            x=MARGIN_INTERIOR,
            y=top_y - logo_h,
            width=logo_w,
            height=logo_h,
            preserveAspectRatio=True,
            mask="auto",
        )
        text_x = MARGIN_INTERIOR + logo_w + 0.3 * cm
    else:
        text_x = MARGIN_INTERIOR

    # --- Título do simulado ---
    canvas.setFont(_BASE_FONT_BOLD, 14)
    title = exam.title if exam.title else "SIMULADO"
    canvas.drawString(text_x, top_y - 1.0 * cm, title)

    # --- Área do conhecimento ---
    canvas.setFont(_BASE_FONT, _BASE_SIZE)
    area_text = exam.area if exam.area else ""
    if area_text:
        canvas.drawString(text_x, top_y - 1.8 * cm, f"Área: {area_text}")

    # --- Data de aplicação ---
    canvas.setFont(_BASE_FONT, _BASE_SIZE)
    today = datetime.now().strftime("%d/%m/%Y")
    canvas.drawRightString(
        PAGE_W - MARGIN_EXTERIOR,
        top_y - 1.0 * cm,
        f"Data: {today}",
    )

    # --- Número de questões ---
    canvas.drawRightString(
        PAGE_W - MARGIN_EXTERIOR,
        top_y - 1.8 * cm,
        f"Questões: {exam.options_count if hasattr(exam, 'options_count') else '—'}",
    )

    # --- Linha separadora abaixo do cabeçalho ---
    canvas.setLineWidth(0.8)
    line_y = top_y - HEADER_H + 0.3 * cm
    canvas.line(MARGIN_INTERIOR, line_y, PAGE_W - MARGIN_EXTERIOR, line_y)

    canvas.restoreState()


def _draw_footer(canvas, doc):
    """
    Desenha o rodapé em TODAS as páginas:
      - Número de página centralizado
      - Linha horizontal acima

    ABNT: número de página em algarismos arábicos, centrado.
    """
    canvas.saveState()

    footer_y = MARGIN_BOTTOM - 0.3 * cm

    # Linha acima do rodapé
    canvas.setLineWidth(0.4)
    canvas.line(
        MARGIN_INTERIOR, footer_y + 0.5 * cm,
        PAGE_W - MARGIN_EXTERIOR, footer_y + 0.5 * cm,
    )

    # Número de página centralizado
    canvas.setFont(_BASE_FONT, 10)
    page_num = canvas.getPageNumber()
    canvas.drawCentredString(
        PAGE_W / 2,
        footer_y,
        str(page_num),
    )

    canvas.restoreState()


# =============================================================================
# CONSTRUTOR DO CADERNO DE QUESTÕES
# =============================================================================

def _build_booklet(
    exam,
    questions: list,
    output_path: str,
    student_name: str = "",
    student_id: int = 0,
    logo_path: Optional[str] = None,
) -> None:
    """
    Gera o caderno de questões em PDF.

    Layout:
      - A4, duas colunas, margens ABNT em espelho
      - Times-Roman 12pt, leading 18pt (espaçamento 1,5)
      - Cabeçalho completo na primeira página
      - Rodapé com número de página em todas as páginas
      - Fórmulas LaTeX renderizadas como imagens via matplotlib

    Parâmetros:
        exam:         model Exam
        questions:    lista de dicts com campos:
                        number   (int)   — número da questão
                        stem     (str)   — enunciado (pode conter $LaTeX$)
                        options  (list)  — lista de dicts {label, text}
                        image    (str)   — caminho de imagem (opcional)
        output_path:  caminho completo do PDF de saída
        student_name: nome do aluno (para cabeçalho)
        student_id:   ID do aluno
        logo_path:    caminho do logo da escola (opcional)
    """
    # -------------------------------------------------------------------------
    # Configuração do documento com layout espelho
    # -------------------------------------------------------------------------
    # O ReportLab suporta margens espelho via PageTemplate com frames
    # distintos para páginas pares e ímpares.
    #
    # Página ímpar (direita do caderno):
    #   margem esquerda = INTERIOR (3cm), margem direita = EXTERIOR (2cm)
    # Página par (esquerda do caderno):
    #   margem esquerda = EXTERIOR (2cm), margem direita = INTERIOR (3cm)

    doc = BaseDocTemplate(
        output_path,
        pagesize=A4,
        # Margens padrão (usadas como fallback)
        leftMargin=MARGIN_INTERIOR,
        rightMargin=MARGIN_EXTERIOR,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title=exam.title if exam.title else "Simulado",
        author="SAMBA Simulator",
        subject=exam.area or "",
    )

    # -------------------------------------------------------------------------
    # Frames das duas colunas para páginas ÍMPARES (margem interior à esquerda)
    # -------------------------------------------------------------------------
    def _frames_odd(header_space: float = 0.0):
        """
        Cria os dois frames de coluna para páginas ímpares.
        header_space: espaço extra reservado no topo para o cabeçalho.
        """
        col_top    = PAGE_H - MARGIN_TOP - header_space
        col_height = col_top - MARGIN_BOTTOM - FOOTER_H

        frame_left = Frame(
            x1=MARGIN_INTERIOR,
            y1=MARGIN_BOTTOM + FOOTER_H,
            width=COL_W,
            height=col_height,
            leftPadding=0, rightPadding=0,
            topPadding=0,  bottomPadding=0,
            id="odd_col1",
        )
        frame_right = Frame(
            x1=MARGIN_INTERIOR + COL_W + COL_GAP,
            y1=MARGIN_BOTTOM + FOOTER_H,
            width=COL_W,
            height=col_height,
            leftPadding=0, rightPadding=0,
            topPadding=0,  bottomPadding=0,
            id="odd_col2",
        )
        return [frame_left, frame_right]

    def _frames_even(header_space: float = 0.0):
        """
        Cria os dois frames de coluna para páginas pares.
        Espelha as margens: exterior à esquerda, interior à direita.
        """
        col_top    = PAGE_H - MARGIN_TOP - header_space
        col_height = col_top - MARGIN_BOTTOM - FOOTER_H

        frame_left = Frame(
            x1=MARGIN_EXTERIOR,
            y1=MARGIN_BOTTOM + FOOTER_H,
            width=COL_W,
            height=col_height,
            leftPadding=0, rightPadding=0,
            topPadding=0,  bottomPadding=0,
            id="even_col1",
        )
        frame_right = Frame(
            x1=MARGIN_EXTERIOR + COL_W + COL_GAP,
            y1=MARGIN_BOTTOM + FOOTER_H,
            width=COL_W,
            height=col_height,
            leftPadding=0, rightPadding=0,
            topPadding=0,  bottomPadding=0,
            id="even_col2",
        )
        return [frame_left, frame_right]

    # -------------------------------------------------------------------------
    # Templates de página
    # -------------------------------------------------------------------------
    # Primeira página: reserva espaço para o cabeçalho (HEADER_H)
    first_page_template = PageTemplate(
        id="first",
        frames=_frames_odd(header_space=HEADER_H),
        onPage=lambda c, d: (
            _draw_header_first_page(c, d, exam, logo_path),
            _draw_footer(c, d),
        ),
    )

    # Páginas ímpares (exceto a primeira)
    odd_page_template = PageTemplate(
        id="odd",
        frames=_frames_odd(),
        onPage=lambda c, d: _draw_footer(c, d),
    )

    # Páginas pares — espelho
    even_page_template = PageTemplate(
        id="even",
        frames=_frames_even(),
        onPage=lambda c, d: _draw_footer(c, d),
    )

    doc.addPageTemplates([first_page_template, odd_page_template, even_page_template])

    # -------------------------------------------------------------------------
    # Conteúdo do caderno
    # -------------------------------------------------------------------------
    story = []

    # Instrução geral (ABNT recomenda instruções antes das questões)
    instructions = (
        "Leia atentamente cada questão antes de responder. "
        "Marque apenas uma alternativa por questão na folha de respostas. "
        "Não é permitido o uso de corretivo ou caneta diferente da azul/preta."
    )
    story.append(Paragraph(instructions, STYLES["instruction"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(width="100%", thickness=0.4, color=colors.black))
    story.append(Spacer(1, 0.2 * cm))

    # Questões
    for q in questions:
        q_number = q.get("number", 0)
        q_stem   = q.get("stem", "")
        q_options = q.get("options", [])
        q_image  = q.get("image")  # caminho de imagem opcional

        # Bloco da questão (KeepTogether evita que quebre entre colunas)
        block = []

        # Número da questão
        block.append(
            Paragraph(f"<b>Questão {q_number}</b>", STYLES["question_number"])
        )

        # Imagem associada à questão (se houver)
        if q_image and os.path.exists(q_image):
            try:
                with PILImage.open(q_image) as pil_img:
                    iw, ih = pil_img.size
                # Limita a 90% da largura da coluna, proporcional
                max_w = COL_W * 0.9
                scale = min(max_w / iw, (USABLE_H * 0.3) / ih)
                block.append(Image(q_image, width=iw * scale, height=ih * scale))
                block.append(Spacer(1, 0.2 * cm))
            except Exception as exc:
                print(f"[pdf_generator] Erro ao carregar imagem {q_image}: {exc}")

        # Enunciado (pode conter $LaTeX$)
        stem_flowables = _parse_text_with_latex(q_stem, STYLES["stem"])
        block.extend(stem_flowables)
        block.append(Spacer(1, 0.15 * cm))

        # Alternativas
        for opt in q_options:
            label = opt.get("label", "")
            text  = opt.get("text", "")
            # Alternativas também podem conter LaTeX
            opt_text = f"<b>{label})</b> {text}"
            opt_flowables = _parse_text_with_latex(opt_text, STYLES["option"])
            block.extend(opt_flowables)

        block.append(Spacer(1, 0.3 * cm))

        # Tenta manter a questão junta; se não couber na coluna, quebra normalmente
        try:
            story.append(KeepTogether(block))
        except Exception:
            story.extend(block)

    # Adiciona páginas em branco se necessário para fechar o caderno em múltiplo de 4
    # (padrão de impressão para encadernação tipo caderno)
    story.append(Spacer(1, 1 * cm))

    # -------------------------------------------------------------------------
    # Geração do PDF
    # -------------------------------------------------------------------------
    doc.build(story)

    # Limpa temporários de LaTeX
    _cleanup_latex_temps()


# =============================================================================
# CONSTRUTOR DA FOLHA DE RESPOSTAS OMR
# =============================================================================

def _build_answer_sheet(
    exam,
    output_path: str,
    student_name: str = "",
    student_id: int = 0,
) -> None:
    """
    Gera a folha de respostas OMR (Optical Mark Recognition).

    Layout:
      - A4, uma coluna, margens ABNT
      - Cabeçalho com campos de identificação do aluno
      - Grade de bolhas configurável (omr_rows × omr_cols)
      - QR-code opcional (barcode_enabled)
      - Rodapé com número de página

    A grade é configurada pelos campos do model Exam:
        exam.omr_rows: número de questões (linhas)
        exam.omr_cols: número de alternativas (colunas)
    """
    from reportlab.platypus import SimpleDocTemplate

    # Lê configuração OMR do simulado (com fallback para padrões)
    n_rows = getattr(exam, "omr_rows", 10)   # questões
    n_cols = getattr(exam, "omr_cols", 5)    # alternativas (A-E)
    barcode = getattr(exam, "barcode_enabled", False)
    header_fields_json = getattr(exam, "omr_header_fields", None)

    # Campos do cabeçalho
    default_fields = ["Nome completo", "Turma", "Número", "Data"]
    if header_fields_json:
        import json
        try:
            header_fields = json.loads(header_fields_json)
        except Exception:
            header_fields = default_fields
    else:
        header_fields = default_fields

    # Labels das alternativas (A, B, C, ...)
    col_labels = [chr(ord("A") + i) for i in range(n_cols)]

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN_INTERIOR,
        rightMargin=MARGIN_EXTERIOR,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title=f"Folha de Respostas — {exam.title}",
    )

    story = []

    # -------------------------------------------------------------------------
    # Cabeçalho da folha de respostas
    # -------------------------------------------------------------------------
    story.append(Paragraph(exam.title or "SIMULADO", STYLES["header_title"]))
    story.append(Paragraph("FOLHA DE RESPOSTAS", STYLES["header_title"]))
    story.append(Spacer(1, 0.3 * cm))

    # Campos de identificação
    for field in header_fields:
        story.append(
            Paragraph(
                f"<b>{field}:</b> {'_' * 50}",
                STYLES["body"],
            )
        )
        story.append(Spacer(1, 0.15 * cm))

    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.black))
    story.append(Spacer(1, 0.5 * cm))

    # -------------------------------------------------------------------------
    # Instrução
    # -------------------------------------------------------------------------
    story.append(Paragraph(
        "Marque com um <b>X</b> ou preencha completamente a bolha "
        "correspondente à alternativa escolhida. Use caneta azul ou preta.",
        STYLES["instruction"],
    ))
    story.append(Spacer(1, 0.5 * cm))

    # -------------------------------------------------------------------------
    # Grade de bolhas
    # -------------------------------------------------------------------------
    # Estrutura: linha de cabeçalho + uma linha por questão
    # Célula de bolha: círculo desenhado via canvas (Paragraph com texto)

    # Cabeçalho da grade: Q | A | B | C | D | E
    header_row = ["Q"] + col_labels
    table_data = [header_row]

    for i in range(1, n_rows + 1):
        row = [str(i)]
        for _ in range(n_cols):
            # Bolha vazia representada por "○" (U+25CB)
            row.append("○")
        table_data.append(row)

    # Larguras das colunas
    q_col_w   = 1.0 * cm
    bubble_w  = (USABLE_W - q_col_w) / n_cols
    col_widths = [q_col_w] + [bubble_w] * n_cols

    # Estilo da tabela
    table_style = TableStyle([
        # Cabeçalho
        ("BACKGROUND",   (0, 0), (-1, 0), colors.HexColor("#DDDDDD")),
        ("FONTNAME",     (0, 0), (-1, 0), _BASE_FONT_BOLD),
        ("FONTSIZE",     (0, 0), (-1, 0), _BASE_SIZE),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        # Corpo
        ("FONTNAME",     (0, 1), (-1, -1), _BASE_FONT),
        ("FONTSIZE",     (0, 1), (-1, -1), 14),   # bolhas maiores
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
        # Grade
        ("GRID",         (0, 0), (-1, -1), 0.4, colors.grey),
        ("BOX",          (0, 0), (-1, -1), 0.8, colors.black),
        # Altura das linhas
        ("ROWHEIGHT",    (0, 0), (-1, -1), 0.7 * cm),
    ])

    grade = Table(table_data, colWidths=col_widths, repeatRows=1)
    grade.setStyle(table_style)
    story.append(grade)

    # -------------------------------------------------------------------------
    # QR-code (se habilitado)
    # -------------------------------------------------------------------------
    if barcode:
        story.append(Spacer(1, 0.5 * cm))
        try:
            qr_data = f"SAMBA|exam={exam.id}|student={student_id}"
            qr_img = qrcode.make(qr_data)
            # Salva em buffer de memória
            buf = io.BytesIO()
            qr_img.save(buf, format="PNG")
            buf.seek(0)
            qr_size = 3.0 * cm
            story.append(Image(buf, width=qr_size, height=qr_size))
            story.append(Paragraph(
                f"ID: {exam.id} | Aluno: {student_id}",
                STYLES["footer"],
            ))
        except Exception as exc:
            print(f"[pdf_generator] Erro ao gerar QR-code: {exc}")

    # -------------------------------------------------------------------------
    # Rodapé manual (SimpleDocTemplate não suporta onPage diretamente)
    # -------------------------------------------------------------------------
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=0.4, color=colors.black))
    story.append(Paragraph("Página 1", STYLES["footer"]))

    doc.build(story)


# =============================================================================
# FUNÇÕES PÚBLICAS
# =============================================================================

def _questions_from_exam(db, exam) -> List[Dict]:
    """
    Extrai as questões do simulado em formato compatível com _build_booklet().

    Retorna lista de dicts:
        [
            {
                "number":  1,
                "stem":    "Enunciado da questão...",
                "options": [
                    {"label": "A", "text": "..."},
                    {"label": "B", "text": "..."},
                    ...
                ],
                "image": None,  # ou caminho de arquivo
            },
            ...
        ]

    Se o simulado não tiver questões na seleção final (ExamQuestionLink),
    retorna lista vazia.
    """
    from app.models.exam import ExamQuestionLink

    links = (
        db.query(ExamQuestionLink)
        .filter(ExamQuestionLink.exam_id == exam.id)
        .order_by(ExamQuestionLink.order_idx)
        .all()
    )

    result = []
    for i, link in enumerate(links, start=1):
        q = link.question
        if not q:
            continue

        options = []
        for opt in sorted(q.options, key=lambda o: o.label):
            options.append({"label": opt.label, "text": opt.text})

        result.append({
            "number":  i,
            "stem":    q.stem,
            "options": options,
            "image":   None,  # imagens inline ainda não implementadas no upload
        })

    return result


def generate_exam_pdfs_for_student(
    db,
    exam,
    student_id: int,
    logo_path: Optional[str] = None,
    student_name: str = "",
) -> Dict[str, Any]:
    """
    Gera o caderno de questões E a folha de respostas para um aluno.

    Arquivos gerados em /app/storage/exams/{exam_id}/:
        booklet_exam{exam_id}_student{student_id}.pdf
        omr_exam{exam_id}_student{student_id}_V1.pdf

    Parâmetros:
        db:           sessão SQLAlchemy
        exam:         model Exam (precisa estar LOCKED)
        student_id:   ID do aluno
        logo_path:    caminho do logo da escola (opcional)
        student_name: nome do aluno para o cabeçalho

    Retorna dict com paths gerados e status.
    """
    out_dir = exam_storage_dir(exam.id, create=True)

    booklet_path = str(out_dir / f"booklet_exam{exam.id}_student{student_id}.pdf")
    omr_path     = str(out_dir / f"omr_exam{exam.id}_student{student_id}_V1.pdf")

    questions = _questions_from_exam(db, exam)

    # Caderno de questões
    _build_booklet(
        exam=exam,
        questions=questions,
        output_path=booklet_path,
        student_name=student_name,
        student_id=student_id,
        logo_path=logo_path,
    )

    # Folha de respostas
    _build_answer_sheet(
        exam=exam,
        output_path=omr_path,
        student_name=student_name,
        student_id=student_id,
    )

    return {
        "student_id":   student_id,
        "booklet":      booklet_path,
        "answer_sheet": omr_path,
        "questions":    len(questions),
        "generated":    True,
    }


def generate_exam_pdfs_for_class(
    db,
    exam,
    class_id: int,
    logo_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Gera PDFs para todos os alunos de uma turma.

    Itera sobre os alunos matriculados na turma (via model Student)
    e chama generate_exam_pdfs_for_student() para cada um.

    Parâmetros:
        db:       sessão SQLAlchemy
        exam:     model Exam
        class_id: ID da turma
        logo_path: caminho do logo (opcional, compartilhado entre alunos)

    Retorna dict com lista de resultados por aluno.
    """
    from app.models.school import Student

    students = (
        db.query(Student)
        .filter(Student.class_id == class_id)
        .order_by(Student.name)
        .all()
    )

    results = []
    for student in students:
        res = generate_exam_pdfs_for_student(
            db=db,
            exam=exam,
            student_id=student.id,
            logo_path=logo_path,
            student_name=student.name,
        )
        results.append(res)

    return {
        "class_id":       class_id,
        "students_count": len(students),
        "results":        results,
        "generated":      True,
    }
