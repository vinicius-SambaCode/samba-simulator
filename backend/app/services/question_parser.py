# -*- coding: utf-8 -*-
"""
app/services/question_parser.py
================================
Parser unificado de questões a partir de texto ou arquivo.

FORMATOS SUPORTADOS
-------------------

Formato A — Natural (como o professor escreve no Word):
    1. Enunciado da questão aqui.
    a) Alternativa A
    b) Alternativa B
    c) Alternativa C
    d) Alternativa D
    e) Alternativa E
    Gabarito: C          ← opcional, qualquer capitalização

Formato B — Técnico (formato original do sistema):
    Q: Enunciado da questão
    A) Alternativa A
    B) Alternativa B
    C) Alternativa C
    D) Alternativa D
    E) Alternativa E
    *GABARITO: C         ← opcional

Separadores entre questões:
    - Linha isolada com '---'
    - Linha em branco dupla
    - Próxima numeração (ex.: '2.' após bloco da questão 1)

Gabarito (opcional em ambos os formatos):
    Gabarito: C
    *GABARITO: C
    Gabarito: c          ← case-insensitive
    * Gabarito: C        ← com espaço após asterisco

FUNÇÕES PÚBLICAS
----------------
    parse_pasted_questions(content: str) -> List[Dict]
        Mantida para compatibilidade com paste endpoint existente.

    parse_text_to_questions(content: str) -> List[Dict]
        Novo parser robusto — detecta formato automaticamente.

    extract_text_from_docx(file_bytes: bytes) -> str
    extract_text_from_pdf(file_bytes: bytes) -> str
    extract_text_from_txt(file_bytes: bytes) -> str
        Extratores de texto por tipo de arquivo.

RETORNO
-------
    List[Dict] onde cada dict tem:
        stem: str                  — enunciado
        options: List[Dict]        — [{"label": "A", "text": "..."}]
        correct_label: str | None  — gabarito ou None
"""

import re
import io
from typing import List, Dict, Optional


# =============================================================================
# Extratores de texto por formato de arquivo
# =============================================================================

def extract_text_from_txt(file_bytes: bytes) -> str:
    """Decodifica TXT tentando UTF-8 e latin-1 como fallback."""
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return file_bytes.decode("latin-1")


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extrai texto de .docx preservando quebras de parágrafo.
    Equações OMML (editor de equações do Word) são convertidas para LaTeX inline ($...$).
    """
    try:
        from docx import Document
    except ImportError:
        raise RuntimeError("python-docx não instalado. Adicione ao requirements.txt.")

    try:
        from app.services.omml_to_latex import paragraph_text_with_math
        _has_omml = True
    except ImportError:
        _has_omml = False

    doc = Document(io.BytesIO(file_bytes))
    paragraphs = []
    for para in doc.paragraphs:
        if _has_omml:
            text = paragraph_text_with_math(para).strip()
        else:
            text = para.text.strip()
        if not text:
            continue
        # Se a linha é só equação LaTeX e há stem anterior, cola ao stem
        _is_math_only = text.startswith("$") and text.endswith("$")
        _is_option    = bool(re.match(r'^[a-eA-E]\)', text))
        if _is_math_only and paragraphs and not _is_option:
            last = paragraphs[-1]
            if not re.match(r'^[a-eA-E]\)', last):
                paragraphs[-1] = last + " " + text
                continue
        paragraphs.append(text)
    return "\n".join(paragraphs)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extrai texto de .pdf usando pdfplumber."""
    try:
        import pdfplumber
    except ImportError:
        raise RuntimeError("pdfplumber não instalado. Execute: pip install pdfplumber")

    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text.strip())
    return "\n".join(text_parts)


# =============================================================================
# Parser principal
# =============================================================================

# Detecta início de questão numerada: "1." "1)" "Questão 1" "QUESTÃO 1"
_RE_QUESTION_START = re.compile(
    r'^(?:quest[aã]o\s+)?(\d+)[.)]\s+(.+)$',
    re.IGNORECASE,
)

# Alternativa no formato natural: "a)" "b)" ... "e)"
_RE_OPT_NATURAL = re.compile(r'^([a-eA-E])\)\s*(.+)$')

# Alternativa no formato técnico: "A)" "B)" ... "E)"
_RE_OPT_TECHNICAL = re.compile(r'^([A-E])\)\s*(.+)$')

# Gabarito em qualquer formato
_RE_GABARITO = re.compile(
    r'^\*?\s*gabarito\s*:\s*([A-Ea-e])\s*$',
    re.IGNORECASE,
)

# Separador explícito ---
_RE_SEPARATOR = re.compile(r'^\s*---\s*$')


def _normalize_label(label: str) -> str:
    """Converte label para maiúsculo (a→A, b→B, ...)."""
    return label.upper()


def _parse_block(lines: List[str]) -> Optional[Dict]:
    """
    Tenta extrair uma questão de uma lista de linhas.
    Retorna None se o bloco não tiver enunciado ou alternativas válidas.
    """
    if not lines:
        return None

    stem_lines = []
    opts = []
    correct = None
    reading_stem = True

    for line in lines:
        # Gabarito
        m_gab = _RE_GABARITO.match(line)
        if m_gab:
            correct = _normalize_label(m_gab.group(1))
            reading_stem = False
            continue

        # Alternativa natural (a, b, c, d, e)
        m_nat = _RE_OPT_NATURAL.match(line)
        if m_nat:
            opts.append({
                "label": _normalize_label(m_nat.group(1)),
                "text": m_nat.group(2).strip(),
            })
            reading_stem = False
            continue

        # Alternativa técnica (A, B, C, D, E) — evita reprocessar naturais
        m_tec = _RE_OPT_TECHNICAL.match(line)
        if m_tec and not m_nat:
            opts.append({
                "label": m_tec.group(1).upper(),
                "text": m_tec.group(2).strip(),
            })
            reading_stem = False
            continue

        # Ainda no enunciado
        if reading_stem:
            stem_lines.append(line)
        # Linhas após alternativas são ignoradas (ex.: espaços extras)

    stem = " ".join(stem_lines).strip()

    # Remove numeração do início do enunciado se vier junto ("1. Enunciado")
    stem = re.sub(r'^\d+[.)]\s*', '', stem).strip()

    if not stem or not opts:
        return None

    # Deduplicar alternativas (caso o parser pegue a mesma duas vezes)
    seen = set()
    unique_opts = []
    for o in opts:
        if o["label"] not in seen:
            seen.add(o["label"])
            unique_opts.append(o)

    return {
        "stem": stem,
        "options": unique_opts,
        "correct_label": correct,
    }


def parse_text_to_questions(content: str) -> List[Dict]:
    """
    Parser robusto — detecta formato automaticamente.

    Estratégia:
    1. Tenta separar por '---' (formato técnico).
    2. Se não encontrar separadores, tenta separar por numeração ("1.", "2.").
    3. Fallback: trata o texto inteiro como uma única questão.
    """
    content = content.strip()
    if not content:
        return []

    # --- Estratégia 1: separador explícito ---
    if _RE_SEPARATOR.search(content, re.MULTILINE):
        raw_blocks = re.split(r'(?m)^\s*---\s*$', content)
        blocks = []
        for raw in raw_blocks:
            lines = [ln.strip() for ln in raw.strip().splitlines() if ln.strip()]
            result = _parse_block(lines)
            if result:
                blocks.append(result)
        if blocks:
            return blocks

    # --- Estratégia 2: separar por numeração ---
    # Agrupa linhas em blocos iniciados por "1." "2." etc.
    all_lines = [ln.strip() for ln in content.splitlines()]
    grouped: List[List[str]] = []
    current: List[str] = []

    for line in all_lines:
        if not line:
            continue
        m = _RE_QUESTION_START.match(line)
        if m:
            if current:
                grouped.append(current)
            # começa novo bloco; enunciado = texto após o número
            stem_start = m.group(2).strip()
            current = [stem_start] if stem_start else []
        else:
            current.append(line)

    if current:
        grouped.append(current)

    if grouped:
        results = []
        for block_lines in grouped:
            result = _parse_block(block_lines)
            if result:
                results.append(result)
        if results:
            return results

    # --- Fallback: bloco único ---
    lines = [ln.strip() for ln in all_lines if ln]
    result = _parse_block(lines)
    return [result] if result else []


def parse_pasted_questions(content: str) -> List[Dict]:
    """
    Mantida para compatibilidade com o endpoint /questions/paste existente.
    Agora delega ao parser robusto.
    """
    return parse_text_to_questions(content)
