# -*- coding: utf-8 -*-
"""
app/services/docx_image_extractor.py
======================================
Extrai imagens embutidas de arquivos .docx e as salva em disco,
vinculando cada imagem à questão correta pela posição no XML.

TIPOS SUPORTADOS
----------------
  PNG, JPEG, GIF, WEBP, BMP → extraídos e salvos
  EMF, WMF                  → IGNORADOS (imagens de equações do Word)

API PÚBLICA
-----------
  extract_images_by_question(file_bytes) -> Dict[int, List[ImageRecord]]
      Extrai imagens agrupadas por índice de questão (0-based).

  extract_images_from_docx(file_bytes) -> List[ImageRecord]
      Compatibilidade — retorna lista plana.

  save_images_to_disk(question_id, records) -> List[dict]
      Salva os binários e retorna dicts prontos para QuestionImage.
"""

import io
import os
import re
import uuid
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict

STORAGE_BASE = "/app/storage"

_MIME_MAP = {
    "png":  "image/png",
    "jpeg": "image/jpeg",
    "jpg":  "image/jpeg",
    "gif":  "image/gif",
    "webp": "image/webp",
    "bmp":  "image/png",
    "emf":  None,
    "wmf":  None,
    "svg":  None,
}

_RE_QUESTION_START = re.compile(r'^\s*(?:quest[aã]o\s+)?(\d+)[.)]\s*', re.IGNORECASE)
_RE_OPTION         = re.compile(r'^\s*([a-eA-E])\)\s*')


@dataclass
class ImageRecord:
    bytes_data:   bytes
    mime_type:    str
    context:      str = "stem"
    order_idx:    int = 0
    width_px:     Optional[int] = None
    height_px:    Optional[int] = None
    ext:          str = "png"
    question_idx: int = 0


def _ext_from_content_type(ct: str) -> str:
    if "jpeg" in ct or "jpg" in ct: return "jpg"
    if "gif"  in ct:                return "gif"
    if "webp" in ct:                return "webp"
    if "bmp"  in ct:                return "bmp"
    return "png"


def _get_image_size(data: bytes) -> Tuple[Optional[int], Optional[int]]:
    try:
        from PIL import Image
        return Image.open(io.BytesIO(data)).size
    except Exception:
        return None, None


def _is_vector(content_type: str) -> bool:
    """True para EMF/WMF (imagens de equações geradas pelo Word)."""
    ct = content_type.lower()
    return any(x in ct for x in ["emf", "wmf", "metafile"])


def extract_images_by_question(file_bytes: bytes) -> Dict[int, List[ImageRecord]]:
    """
    Extrai imagens agrupadas por índice de questão (0-based).
    A vinculação usa a posição dos parágrafos no XML.
    """
    try:
        from docx import Document
        from docx.oxml.ns import qn
    except ImportError:
        raise RuntimeError("python-docx não instalado.")

    doc = Document(io.BytesIO(file_bytes))
    result:           Dict[int, List[ImageRecord]] = {}
    context_counters: Dict[str, int] = {}
    current_q_idx   = -1
    current_context = "stem"
    seen_rids:  set = set()

    for para_idx, para in enumerate(doc.paragraphs):
        text = para.text.strip()

        # Nova questão?
        m_q = _RE_QUESTION_START.match(text)
        if m_q and len(text) > len(m_q.group(0)):
            current_q_idx  += 1
            current_context = "stem"
            context_counters = {}

        # Nova alternativa?
        m_opt = _RE_OPTION.match(text)
        if m_opt and current_q_idx >= 0:
            new_ctx = f"option_{m_opt.group(1).upper()}"
            if new_ctx != current_context:
                current_context = new_ctx
                context_counters[current_context] = 0

        # Imagens no parágrafo
        for elem in para._element.iter():
            if elem.tag != qn('a:blip'):
                continue
            r_embed = elem.get(qn('r:embed'))
            if not r_embed:
                continue
            # Chave única por parágrafo + rId (permite mesma imagem em questões diferentes)
            rid_key = (para_idx, r_embed)
            if rid_key in seen_rids:
                continue
            try:
                part = para.part.rels[r_embed].target_part
            except (KeyError, AttributeError):
                continue

            ct = part.content_type.lower()
            if _is_vector(ct):
                continue   # ignora EMF/WMF

            ext  = _ext_from_content_type(ct)
            mime = _MIME_MAP.get(ext)
            if mime is None:
                continue

            seen_rids.add(rid_key)
            img_bytes = part.blob
            w, h = _get_image_size(img_bytes)
            idx  = context_counters.get(current_context, 0)
            context_counters[current_context] = idx + 1
            q_idx = max(current_q_idx, 0)

            result.setdefault(q_idx, []).append(ImageRecord(
                bytes_data=img_bytes, mime_type=mime,
                context=current_context, order_idx=idx,
                width_px=w, height_px=h, ext=ext, question_idx=q_idx,
            ))

    return result


def extract_images_from_docx(file_bytes: bytes) -> List[ImageRecord]:
    """Compatibilidade — retorna lista plana de todos os ImageRecord."""
    result = []
    for recs in extract_images_by_question(file_bytes).values():
        result.extend(recs)
    return result


def save_images_to_disk(question_id: int, records: List[ImageRecord]) -> List[dict]:
    """Salva binários em disco e retorna dicts para QuestionImage."""
    folder = os.path.join(STORAGE_BASE, "questions", str(question_id))
    os.makedirs(folder, exist_ok=True)
    saved = []
    for rec in records:
        uid      = uuid.uuid4().hex[:8]
        filename = f"img_{rec.context}_{rec.order_idx}_{uid}.{rec.ext}"
        abs_path = os.path.join(folder, filename)
        with open(abs_path, "wb") as f:
            f.write(rec.bytes_data)
        saved.append({
            "storage_path": f"questions/{question_id}/{filename}",
            "mime_type":    rec.mime_type,
            "context":      rec.context,
            "order_idx":    rec.order_idx,
            "width_px":     rec.width_px,
            "height_px":    rec.height_px,
        })
    return saved
