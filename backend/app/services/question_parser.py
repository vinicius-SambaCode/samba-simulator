# -*- coding: utf-8 -*-
"""
Parser simples de texto colado/TXT (Sprint 1)
- Identifica blocos de questão por separador '---' (linha isolada)
- Cada bloco deve conter:
  'Q:' para enunciado
  Linhas iniciando com 'A)'...'E)' para alternativas
  Opcional: linha '*GABARITO: X' (X = A..E)

Validações fortes de quantidade de alternativas virão na rota (conforme options_count do Exam).
"""

import re
from typing import List, Dict, Optional


def parse_pasted_questions(content: str) -> List[Dict]:
    blocks = re.split(r'(?m)^\s*---\s*$', content.strip())
    out = []
    for raw in blocks:
        lines = [ln.strip() for ln in raw.strip().splitlines() if ln.strip()]
        if not lines:
            continue

        # Enunciado (Q:)
        if not lines[0].lower().startswith("q:"):
            raise ValueError("Bloco de questão sem 'Q:' no início.")
        stem = lines[0][2:].strip()

        # Alternativas A) .. E)
        opts = []
        correct = None
        for ln in lines[1:]:
            m = re.match(r'^([A-E])\)\s*(.+)$', ln)
            if m:
                opts.append({"label": m.group(1), "text": m.group(2)})
                continue
            m2 = re.match(r'^\*GABARITO:\s*([A-E])\s*$', ln, flags=re.IGNORECASE)
            if m2:
                correct = m2.group(1).upper()
                continue

        out.append({"stem": stem, "options": opts, "correct_label": correct})
    return out