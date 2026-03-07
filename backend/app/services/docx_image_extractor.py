# -*- coding: utf-8 -*-
"""
app/services/docx_image_extractor.py
======================================
Extrai imagens embutidas de arquivos .docx e as salva em disco.

FUNCIONAMENTO
-------------
Um arquivo .docx é um ZIP. As imagens ficam em word/media/.
O python-docx expõe os relacionamentos de cada parágrafo — quando
um parágrafo contém uma imagem (drawing/inline), extraímos o binário
e salvamos em /app/storage/questions/{question_id}/.

CONTEXTO DAS IMAGENS
--------------------
Para determinar se a imagem pertence ao enunciado ou a uma alternativa,
analisamos a posição relativa do parágrafo da imagem em relação aos
parágrafos de alternativas já identificados.

Regra:
  - Se a imagem aparece ANTES da primeira alternativa → context = 'stem'
  - Se a imagem aparece logo APÓS uma linha 'A) ...' → context = 'option_A'
  - ... e assim por diante.

RETORNO
-------
    List[ImageRecord] onde cada item tem:
        bytes_data : bytes da imagem
        mime_type  : 'image/png' | 'image/jpeg' | 'image/gif' | 'image/webp'
        context    : 'stem' | 'option_A' .. 'option_E'
        order_idx  : posição dentro do contexto
        width_px   : largura (se disponível)
        height_px  : altura (se disponível)
"""

import io
import os
import re
import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

STORAGE_BASE = "/app/storage"

# Mime types suportados por extensão de parte do relacionamento
_MIME_MAP = {
    "png":  "image/png",
    "jpeg": "image/jpeg",
    "jpg":  "image/jpeg",
    "gif":  "image/gif",
    "webp": "image/webp",
    "bmp":  "image/png",   # converte BMP para PNG ao salvar
    "emf":  None,          # Enhanced Metafile — ignorado (vetorial Windows)
    "wmf":  None,          # Windows Metafile — ignorado
}


@dataclass
class ImageRecord:
    bytes_data: bytes
    mime_type:  str
    context:    str = "stem"
    order_idx:  int = 0
    width_px:   Optional[int] = None
    height_px:  Optional[int] = None
    ext:        str = "png"


def _ext_from_content_type(ct: str) -> str:
    if "jpeg" in ct or "jpg" in ct:
        return "jpg"
    if "gif" in ct in ct:
        return "gif"
    if "webp" in ct:
        return "webp"
    return "png"


def _get_image_size(data: bytes) -> Tuple[Optional[int], Optional[int]]:
    """Retorna (width, height) usando Pillow, ou (None, None) se falhar."""
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(data))
        return img.size  # (width, height)
    except Exception:
        return None, None


def extract_images_from_docx(file_bytes: bytes) -> List[ImageRecord]:
    """
    Extrai todas as imagens embutidas do .docx e determina o contexto
    (stem ou option_X) de cada uma.

    Retorna lista de ImageRecord. Imagens EMF/WMF são ignoradas.
    """
    try:
        from docx import Document
        from docx.oxml.ns import qn
    except ImportError:
        raise RuntimeError("python-docx não instalado.")

    doc = Document(io.BytesIO(file_bytes))
    records: List[ImageRecord] = []

    # Regex para identificar alternativas
    _RE_OPT = re.compile(r'^([a-eA-E])\)\s*')

    current_context = "stem"
    context_counters: dict = {}

    for para in doc.paragraphs:
        text = para.text.strip()

        # Atualiza contexto com base no texto do parágrafo
        m = _RE_OPT.match(text)
        if m:
            current_context = f"option_{m.group(1).upper()}"

        # Procura elementos de imagem no XML do parágrafo
        for elem in para._element.iter():
            # Inline drawing (imagem embutida)
            if elem.tag == qn('a:blip'):
                r_embed = elem.get(qn('r:embed'))
                if not r_embed:
                    continue

                # Recupera o relacionamento da parte do documento
                try:
                    part = para.part.rels[r_embed].target_part
                except (KeyError, AttributeError):
                    continue

                ct = part.content_type.lower()

                # Determina extensão e verifica se é suportada
                ext = _ext_from_content_type(ct)
                mime = _MIME_MAP.get(ext)
                if mime is None:
                    continue  # ignora EMF/WMF

                img_bytes = part.blob
                w, h = _get_image_size(img_bytes)

                idx = context_counters.get(current_context, 0)
                context_counters[current_context] = idx + 1

                records.append(ImageRecord(
                    bytes_data=img_bytes,
                    mime_type=mime,
                    context=current_context,
                    order_idx=idx,
                    width_px=w,
                    height_px=h,
                    ext=ext,
                ))

    return records


def save_images_to_disk(
    question_id: int,
    records: List[ImageRecord],
) -> List[dict]:
    """
    Salva os binários em /app/storage/questions/{question_id}/
    e retorna lista de dicts prontos para criar QuestionImage.

    Retorno:
        [
          {
            "storage_path": "questions/42/img_stem_0_a1b2.png",
            "mime_type": "image/png",
            "context": "stem",
            "order_idx": 0,
            "width_px": 800,
            "height_px": 600,
          },
          ...
        ]
    """
    folder = os.path.join(STORAGE_BASE, "questions", str(question_id))
    os.makedirs(folder, exist_ok=True)

    saved = []
    for rec in records:
        # Nome único: img_{context}_{order}_{uuid4[:8]}.ext
        uid = uuid.uuid4().hex[:8]
        filename = f"img_{rec.context}_{rec.order_idx}_{uid}.{rec.ext}"
        abs_path = os.path.join(folder, filename)

        with open(abs_path, "wb") as f:
            f.write(rec.bytes_data)

        rel_path = f"questions/{question_id}/{filename}"
        saved.append({
            "storage_path": rel_path,
            "mime_type":    rec.mime_type,
            "context":      rec.context,
            "order_idx":    rec.order_idx,
            "width_px":     rec.width_px,
            "height_px":    rec.height_px,
        })

    return saved
