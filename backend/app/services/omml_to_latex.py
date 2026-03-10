# -*- coding: utf-8 -*-
"""
app/services/omml_to_latex.py
==============================
Converte equações OMML (Office Math Markup Language) para LaTeX.

OMML é o formato XML interno do Microsoft Word para equações criadas
com o editor de equações nativo (Insert → Equation).

ESTRUTURAS SUPORTADAS
---------------------
  m:f        → fração  \\frac{num}{den}
  m:sSup     → sobrescrito  base^{exp}
  m:sSub     → subscrito  base_{sub}
  m:sSubSup  → sub+sobrescrito  base_{sub}^{sup}
  m:nary     → operador n-ário (∫, ∑, ∏)
  m:rad      → raiz  \\sqrt[n]{base}
  m:d        → delimitadores (parênteses, colchetes, chaves)
  m:func     → função aplicada (sin, cos, lim...)
  m:eqArr    → array de equações (alinhamento)
  m:m        → matriz
  m:r / m:t  → texto/símbolo corrido

USO
---
    from app.services.omml_to_latex import omml_para_to_latex, extract_math_from_paragraph

    # De um elemento m:oMathPara do lxml:
    latex = omml_para_to_latex(omath_para_element)
    # → "$e^x = 1 + \\frac{x}{1!} + \\frac{x^2}{2!} + \\cdots$"

    # De um parágrafo python-docx:
    latex_list = extract_math_from_paragraph(paragraph)
    # → lista de strings LaTeX, uma por equação no parágrafo

INTEGRAÇÃO COM O PARSER
-----------------------
O `question_parser.py` deve chamar `extract_math_from_paragraph()` para
cada parágrafo do documento antes de montar o texto da questão.
As equações são inseridas inline como $...$.
"""

from __future__ import annotations
from typing import Optional
from lxml import etree

# Namespace OMML
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"

def _tag(local: str) -> str:
    return f"{{{M}}}{local}"


# =============================================================================
# MAPA DE SÍMBOLOS OMML → LaTeX
# =============================================================================

# Operadores n-ários (m:nary → m:chr)
_NARY_MAP = {
    "∫":  r"\int",
    "∬":  r"\iint",
    "∭":  r"\iiint",
    "∮":  r"\oint",
    "∑":  r"\sum",
    "∏":  r"\prod",
    "⋃":  r"\bigcup",
    "⋂":  r"\bigcap",
    "⋁":  r"\bigvee",
    "⋀":  r"\bigwedge",
    "":   r"\int",   # fallback sem chr
}

# Símbolos Unicode → LaTeX (dentro de m:t)
_SYMBOL_MAP = {
    "∞":  r"\infty",
    "≤":  r"\leq",
    "≥":  r"\geq",
    "≠":  r"\neq",
    "≈":  r"\approx",
    "±":  r"\pm",
    "∓":  r"\mp",
    "×":  r"\times",
    "÷":  r"\div",
    "·":  r"\cdot",
    "…":  r"\ldots",
    "⋯":  r"\cdots",
    "→":  r"\rightarrow",
    "←":  r"\leftarrow",
    "↔":  r"\leftrightarrow",
    "⇒":  r"\Rightarrow",
    "⇔":  r"\Leftrightarrow",
    "∈":  r"\in",
    "∉":  r"\notin",
    "⊂":  r"\subset",
    "⊃":  r"\supset",
    "⊆":  r"\subseteq",
    "⊇":  r"\supseteq",
    "∅":  r"\emptyset",
    "∪":  r"\cup",
    "∩":  r"\cap",
    "∧":  r"\wedge",
    "∨":  r"\vee",
    "¬":  r"\neg",
    "∀":  r"\forall",
    "∃":  r"\exists",
    "∂":  r"\partial",
    "∇":  r"\nabla",
    "α":  r"\alpha",
    "β":  r"\beta",
    "γ":  r"\gamma",
    "δ":  r"\delta",
    "ε":  r"\epsilon",
    "ζ":  r"\zeta",
    "η":  r"\eta",
    "θ":  r"\theta",
    "ι":  r"\iota",
    "κ":  r"\kappa",
    "λ":  r"\lambda",
    "μ":  r"\mu",
    "ν":  r"\nu",
    "ξ":  r"\xi",
    "π":  r"\pi",
    "ρ":  r"\rho",
    "σ":  r"\sigma",
    "τ":  r"\tau",
    "υ":  r"\upsilon",
    "φ":  r"\phi",
    "χ":  r"\chi",
    "ψ":  r"\psi",
    "ω":  r"\omega",
    "Γ":  r"\Gamma",
    "Δ":  r"\Delta",
    "Θ":  r"\Theta",
    "Λ":  r"\Lambda",
    "Ξ":  r"\Xi",
    "Π":  r"\Pi",
    "Σ":  r"\Sigma",
    "Υ":  r"\Upsilon",
    "Φ":  r"\Phi",
    "Ψ":  r"\Psi",
    "Ω":  r"\Omega",
}

# Delimitadores (m:d → m:dPr → m:begChr / m:endChr)
_DELIM_MAP = {
    ("(", ")"):  (r"\left(", r"\right)"),
    ("[", "]"):  (r"\left[", r"\right]"),
    ("{", "}"):  (r"\left\{", r"\right\}"),
    ("|", "|"):  (r"\left|", r"\right|"),
    ("‖", "‖"): (r"\left\|", r"\right\|"),
    ("⌈", "⌉"): (r"\left\lceil", r"\right\rceil"),
    ("⌊", "⌋"): (r"\left\lfloor", r"\right\rfloor"),
    ("", ")"):   (r"\left(", r"\right)"),
    ("(", ""):   (r"\left(", r"\right)"),
    ("", ""):    ("", ""),
}


# =============================================================================
# CONVERSOR PRINCIPAL
# =============================================================================

def _convert_text(text: str) -> str:
    """Converte caracteres especiais Unicode para LaTeX."""
    result = []
    for ch in text:
        result.append(_SYMBOL_MAP.get(ch, ch))
    return "".join(result)


def _convert_element(elem) -> str:
    """
    Converte recursivamente um elemento OMML para LaTeX.
    Dispatcher central — chama o handler específico por tag.
    """
    tag = elem.tag

    if tag == _tag("oMathPara"):
        return _conv_oMathPara(elem)
    elif tag == _tag("oMath"):
        return _conv_oMath(elem)
    elif tag == _tag("f"):
        return _conv_fraction(elem)
    elif tag == _tag("sSup"):
        return _conv_ssup(elem)
    elif tag == _tag("sSub"):
        return _conv_ssub(elem)
    elif tag == _tag("sSubSup"):
        return _conv_ssubsup(elem)
    elif tag == _tag("nary"):
        return _conv_nary(elem)
    elif tag == _tag("rad"):
        return _conv_rad(elem)
    elif tag == _tag("d"):
        return _conv_delim(elem)
    elif tag == _tag("func"):
        return _conv_func(elem)
    elif tag == _tag("eqArr"):
        return _conv_eqarr(elem)
    elif tag == _tag("m"):
        return _conv_matrix(elem)
    elif tag == _tag("r"):
        return _conv_run(elem)
    elif tag == _tag("t"):
        return _convert_text(elem.text or "")
    elif tag == _tag("e") or tag == _tag("num") or tag == _tag("den") or \
         tag == _tag("base") or tag == _tag("sub") or tag == _tag("sup") or \
         tag == _tag("deg"):
        # Containers — converte filhos
        return "".join(_convert_element(c) for c in elem)
    else:
        # Tag desconhecida — tenta extrair texto dos filhos
        return "".join(_convert_element(c) for c in elem)


def _children_latex(elem) -> str:
    """Converte todos os filhos de um elemento e concatena."""
    return "".join(_convert_element(c) for c in elem)


def _wrap(latex: str) -> str:
    """Envolve em chaves se necessário (mais de 1 char)."""
    if len(latex) <= 1:
        return latex
    return "{" + latex + "}"


# =============================================================================
# HANDLERS POR TAG
# =============================================================================

def _conv_oMathPara(elem) -> str:
    parts = []
    for child in elem:
        if child.tag == _tag("oMath"):
            parts.append(_conv_oMath(child))
    return " ".join(parts)


def _conv_oMath(elem) -> str:
    return _children_latex(elem)


def _conv_fraction(elem) -> str:
    """m:f → \\frac{num}{den}"""
    num = elem.find(_tag("num"))
    den = elem.find(_tag("den"))
    num_latex = _children_latex(num) if num is not None else ""
    den_latex = _children_latex(den) if den is not None else ""
    return rf"\frac{{{num_latex}}}{{{den_latex}}}"


def _conv_ssup(elem) -> str:
    """m:sSup → base^{sup}"""
    e   = elem.find(_tag("e"))
    sup = elem.find(_tag("sup"))
    base_latex = _children_latex(e)   if e   is not None else ""
    sup_latex  = _children_latex(sup) if sup is not None else ""
    return f"{base_latex}^{_wrap(sup_latex)}"


def _conv_ssub(elem) -> str:
    """m:sSub → base_{sub}"""
    e   = elem.find(_tag("e"))
    sub = elem.find(_tag("sub"))
    base_latex = _children_latex(e)   if e   is not None else ""
    sub_latex  = _children_latex(sub) if sub is not None else ""
    return f"{base_latex}_{_wrap(sub_latex)}"


def _conv_ssubsup(elem) -> str:
    """m:sSubSup → base_{sub}^{sup}"""
    e   = elem.find(_tag("e"))
    sub = elem.find(_tag("sub"))
    sup = elem.find(_tag("sup"))
    base_latex = _children_latex(e)   if e   is not None else ""
    sub_latex  = _children_latex(sub) if sub is not None else ""
    sup_latex  = _children_latex(sup) if sup is not None else ""
    return f"{base_latex}_{_wrap(sub_latex)}^{_wrap(sup_latex)}"


def _conv_nary(elem) -> str:
    """
    m:nary → operador n-ário (∫, ∑, ∏, etc.)
    Estrutura: m:naryPr (propriedades) + m:sub + m:sup + m:e (corpo)
    """
    nary_pr = elem.find(_tag("naryPr"))
    chr_elem = nary_pr.find(_tag("chr")) if nary_pr is not None else None
    operator_char = chr_elem.get(_tag("val"), "∫") if chr_elem is not None else "∫"
    operator = _NARY_MAP.get(operator_char, r"\int")

    sub_elem = elem.find(_tag("sub"))
    sup_elem = elem.find(_tag("sup"))
    e_elem   = elem.find(_tag("e"))

    sub_latex  = _children_latex(sub_elem) if sub_elem is not None else ""
    sup_latex  = _children_latex(sup_elem) if sup_elem is not None else ""
    body_latex = _children_latex(e_elem)   if e_elem   is not None else ""

    result = operator
    if sub_latex:
        result += f"_{{{sub_latex}}}"
    if sup_latex:
        result += f"^{{{sup_latex}}}"
    if body_latex:
        result += f" {body_latex}"
    return result


def _conv_rad(elem) -> str:
    """m:rad → \\sqrt[deg]{base}  ou  \\sqrt{base}"""
    deg_elem  = elem.find(_tag("deg"))
    base_elem = elem.find(_tag("e"))
    base_latex = _children_latex(base_elem) if base_elem is not None else ""

    # Se o grau está vazio (raiz quadrada simples)
    if deg_elem is not None:
        deg_text = _children_latex(deg_elem).strip()
        if deg_text and deg_text != "2":
            return rf"\sqrt[{deg_text}]{{{base_latex}}}"

    return rf"\sqrt{{{base_latex}}}"


def _conv_delim(elem) -> str:
    """m:d → delimitadores \\left( ... \\right)"""
    dpr = elem.find(_tag("dPr"))
    beg = ""
    end = ""
    if dpr is not None:
        beg_elem = dpr.find(_tag("begChr"))
        end_elem = dpr.find(_tag("endChr"))
        beg = beg_elem.get(_tag("val"), "(") if beg_elem is not None else "("
        end = end_elem.get(_tag("val"), ")") if end_elem is not None else ")"

    left, right = _DELIM_MAP.get((beg, end), (rf"\left{beg}", rf"\right{end}"))

    # Conteúdo: um ou mais m:e separados por separador
    contents = []
    for e in elem.findall(_tag("e")):
        contents.append(_children_latex(e))

    inner = ", ".join(contents)
    if left or right:
        return f"{left} {inner} {right}"
    return inner


def _conv_func(elem) -> str:
    """m:func → nome_função {argumento}"""
    fname_elem = elem.find(_tag("fName"))
    e_elem     = elem.find(_tag("e"))
    fname = _children_latex(fname_elem) if fname_elem is not None else ""
    arg   = _children_latex(e_elem)     if e_elem     is not None else ""

    # Funções conhecidas → comando LaTeX
    _func_map = {
        "sin": r"\sin", "cos": r"\cos", "tan": r"\tan",
        "cot": r"\cot", "sec": r"\sec", "csc": r"\csc",
        "arcsin": r"\arcsin", "arccos": r"\arccos", "arctan": r"\arctan",
        "sinh": r"\sinh", "cosh": r"\cosh", "tanh": r"\tanh",
        "log": r"\log", "ln": r"\ln", "exp": r"\exp",
        "lim": r"\lim", "max": r"\max", "min": r"\min",
        "det": r"\det", "dim": r"\dim", "ker": r"\ker",
        "gcd": r"\gcd", "lcm": r"\operatorname{lcm}",
    }
    fname_clean = fname.strip().replace("\\", "")
    latex_fname = _func_map.get(fname_clean, rf"\operatorname{{{fname_clean}}}")
    return rf"{latex_fname} {arg}"


def _conv_eqarr(elem) -> str:
    """m:eqArr → array de equações alinhadas"""
    rows = []
    for e in elem.findall(_tag("e")):
        rows.append(_children_latex(e))
    if len(rows) == 1:
        return rows[0]
    inner = r" \\ ".join(rows)
    return rf"\begin{{aligned}} {inner} \end{{aligned}}"


def _conv_matrix(elem) -> str:
    """m:m → matriz LaTeX"""
    rows = []
    for mr in elem.findall(_tag("mr")):
        cols = []
        for e in mr.findall(_tag("e")):
            cols.append(_children_latex(e))
        rows.append(" & ".join(cols))
    n_cols = max(len(r.split("&")) for r in rows) if rows else 1
    inner = r" \\ ".join(rows)
    return rf"\begin{{pmatrix}} {inner} \end{{pmatrix}}"


def _conv_run(elem) -> str:
    """m:r → run de texto matemático"""
    parts = []
    for child in elem:
        if child.tag == _tag("t"):
            parts.append(_convert_text(child.text or ""))
        # m:rPr (propriedades) é ignorado
    return "".join(parts)


# =============================================================================
# API PÚBLICA
# =============================================================================

def omml_element_to_latex(omath_elem) -> str:
    """
    Converte um elemento m:oMath ou m:oMathPara para uma string LaTeX.

    Parâmetro:
        omath_elem: elemento lxml de tag m:oMath ou m:oMathPara

    Retorna:
        String LaTeX sem delimitadores $ (o chamador decide se é inline ou display).
        Exemplo: r"e^{x} = 1 + \\frac{x}{1!} + \\frac{x^2}{2!} + \\cdots"
    """
    try:
        return _convert_element(omath_elem).strip()
    except Exception as exc:
        # Fallback: extrai texto puro
        raw = "".join(omath_elem.itertext()).strip()
        return raw


def omml_para_to_latex(omath_para_elem) -> str:
    """
    Converte um elemento m:oMathPara para LaTeX inline ($...$).

    Retorna:
        String no formato "$latex$" pronta para inserção no texto.
    """
    latex = omml_element_to_latex(omath_para_elem)
    if latex:
        return f"${latex}$"
    return ""


def extract_math_from_paragraph(paragraph) -> list[str]:
    """
    Extrai todas as equações OMML de um parágrafo python-docx e as converte para LaTeX.

    Parâmetro:
        paragraph: objeto Paragraph do python-docx

    Retorna:
        Lista de strings LaTeX no formato "$...$", uma por equação encontrada.
        Lista vazia se não houver equações.

    Exemplo de uso no parser:
        for para in doc.paragraphs:
            math_list = extract_math_from_paragraph(para)
            if math_list:
                # insere as equações no texto da questão
    """
    results = []
    for elem in paragraph._element.iter():
        if elem.tag == _tag("oMathPara"):
            latex = omml_para_to_latex(elem)
            if latex:
                results.append(latex)
        elif elem.tag == _tag("oMath"):
            # oMath solto (não dentro de oMathPara)
            parent_tags = {a.tag for a in elem.iterancestors()}
            if _tag("oMathPara") not in parent_tags:
                latex = omml_element_to_latex(elem)
                if latex:
                    results.append(f"${latex}$")
    return results


def paragraph_text_with_math(paragraph) -> str:
    """
    Extrai o texto completo de um parágrafo python-docx, substituindo
    equações OMML por LaTeX inline ($...$).

    Este é o método principal para uso no question_parser.py.

    Parâmetro:
        paragraph: objeto Paragraph do python-docx

    Retorna:
        String com o texto do parágrafo, equações convertidas para $LaTeX$.

    Exemplo:
        "A série de Taylor de $e^{x}$ é $1 + x + \\frac{x^2}{2!} + \\cdots$"
    """
    parts = []

    for child in paragraph._element:
        tag = child.tag

        if tag == _tag("oMathPara"):
            latex = omml_para_to_latex(child)
            if latex:
                parts.append(latex)

        elif tag == _tag("oMath"):
            latex_str = omml_element_to_latex(child)
            if latex_str:
                parts.append(f"${latex_str}$")

        else:
            # Elemento normal (w:r, w:hyperlink, etc.) — extrai texto puro
            # Percorre apenas os w:t dentro deste elemento
            W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            for t in child.iter(f"{{{W}}}t"):
                if t.text:
                    parts.append(t.text)

    return "".join(parts)
