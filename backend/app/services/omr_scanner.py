# app/services/omr_scanner.py
# -*- coding: utf-8 -*-
"""
OMR Scanner — lê PDF escaneado, identifica aluno via barcode,
detecta bolhas preenchidas com OpenCV e salva StudentAnswer.

Fluxo:
  1. Converte cada página do PDF em imagem (via pdf2image / fallback pillow)
  2. Lê barcode Code128 → extrai exam_id + student_id
  3. Localiza região do grid de bolhas
  4. Para cada questão detecta qual alternativa está preenchida
  5. Salva StudentAnswer com is_correct calculado contra correct_label
"""

from __future__ import annotations
import os
import io
import re
import logging
import tempfile
from typing import Optional

import cv2
import numpy as np

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes de detecção
# ---------------------------------------------------------------------------
FILL_THRESHOLD   = 0.38   # fração mínima de pixels escuros para considerar bolha marcada
MIN_CIRCLE_AREA  = 80     # área mínima de contorno para ser uma bolha
MAX_CIRCLE_AREA  = 2500   # área máxima


# ---------------------------------------------------------------------------
# PDF → imagens
# ---------------------------------------------------------------------------
def _pdf_to_images(pdf_bytes: bytes) -> list[np.ndarray]:
    """Converte bytes de PDF em lista de imagens OpenCV (BGR)."""
    images = []
    try:
        from pdf2image import convert_from_bytes
        pil_imgs = convert_from_bytes(pdf_bytes, dpi=200)
        for pil in pil_imgs:
            arr = np.array(pil.convert("RGB"))
            images.append(cv2.cvtColor(arr, cv2.COLOR_RGB2BGR))
        return images
    except ImportError:
        pass

    # Fallback: pypdf extrai páginas como imagens (qualidade menor)
    try:
        from pypdf import PdfReader
        import PIL.Image as PILImage
        reader = PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            for img_obj in page.images:
                arr = np.array(PILImage.open(io.BytesIO(img_obj.data)).convert("RGB"))
                images.append(cv2.cvtColor(arr, cv2.COLOR_RGB2BGR))
                break  # uma imagem por página
        return images
    except Exception as e:
        log.warning(f"[omr_scanner] fallback pdf→image falhou: {e}")
        return []


# ---------------------------------------------------------------------------
# Leitura de barcode
# ---------------------------------------------------------------------------
def _read_barcode(image: np.ndarray) -> Optional[str]:
    """Tenta ler barcode Code128 na imagem. Retorna string ou None."""
    # Tenta pyzbar primeiro
    try:
        from pyzbar.pyzbar import decode as pyzbar_decode
        decoded = pyzbar_decode(image)
        for d in decoded:
            return d.data.decode("utf-8")
    except ImportError:
        pass

    # Fallback: OpenCV WeChat QRCode (para QR codes)
    try:
        detector = cv2.wechat_qrcode_WeChatQRCode()
        texts, _ = detector.detectAndDecode(image)
        if texts:
            return texts[0]
    except Exception:
        pass

    return None


def _parse_barcode(barcode_str: str) -> tuple[Optional[int], Optional[int]]:
    """
    Extrai (exam_id, student_id) do barcode.
    Formato: SAMBA-E{exam_id}-S{student_id}
    """
    m = re.match(r"SAMBA-E(\d+)-S(\d+)", barcode_str or "")
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None


# ---------------------------------------------------------------------------
# Detecção de bolhas
# ---------------------------------------------------------------------------
def _preprocess(image: np.ndarray) -> np.ndarray:
    """Converte para cinza, binariza e retorna imagem processada."""
    gray  = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur  = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return thresh


def _find_bubble_grid(thresh: np.ndarray) -> Optional[tuple[int, int, int, int]]:
    """
    Localiza o retângulo que contém o grid de bolhas.
    Estratégia: maior contorno retangular na metade inferior da página.
    Retorna (x, y, w, h) ou None.
    """
    h_img, w_img = thresh.shape
    # Procura na metade inferior (abaixo do cabeçalho)
    roi = thresh[h_img // 3:, :]
    contours, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best = None
    best_area = 0
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        aspect = w / h if h > 0 else 0
        # Grid deve ser largo (aspect > 1.5) e grande
        if area > best_area and aspect > 1.5 and w > w_img * 0.5:
            best_area = area
            best = (x, y + h_img // 3, w, h)  # ajusta offset do ROI

    return best


def _detect_filled_bubbles(
    thresh: np.ndarray,
    grid_rect: tuple[int, int, int, int],
    n_questions: int,
    n_options: int = 5,
    n_cols: int = 0,
) -> dict[int, Optional[str]]:
    """
    Detecta bolhas preenchidas dentro do grid.
    Retorna dict {question_number (1-based): letra_marcada_ou_None}
    """
    OPTIONS = ["A", "B", "C", "D", "E"]
    x0, y0, gw, gh = grid_rect

    # Colunas automáticas (mesma lógica do pdf_generator)
    if not n_cols:
        if n_questions <= 30:
            n_cols = 2
        elif n_questions <= 60:
            n_cols = 3
        else:
            n_cols = 4

    rows_per_col = -(-n_questions // n_cols)  # ceil

    col_w  = gw / n_cols
    row_h  = gh / (rows_per_col + 1)  # +1 para linha de cabeçalho
    opt_w  = col_w * 0.75 / n_options
    num_w  = col_w * 0.20

    results: dict[int, Optional[str]] = {}

    for gc in range(n_cols):
        for row in range(rows_per_col):
            q_num = gc * rows_per_col + row + 1
            if q_num > n_questions:
                break

            # Centro Y da linha (pula linha de cabeçalho)
            cy = int(y0 + (row + 1.5) * row_h)
            # X inicial das bolhas desta coluna
            bx_start = int(x0 + gc * col_w + num_w * col_w)

            filled_opt = None
            best_fill  = FILL_THRESHOLD  # mínimo para considerar marcado

            for oi in range(n_options):
                cx = int(bx_start + (oi + 0.5) * opt_w)
                r  = int(min(opt_w, row_h) * 0.35)

                # Recorte ao redor do círculo
                y1 = max(0, cy - r)
                y2 = min(thresh.shape[0], cy + r)
                x1 = max(0, cx - r)
                x2 = min(thresh.shape[1], cx + r)

                roi_circle = thresh[y1:y2, x1:x2]
                if roi_circle.size == 0:
                    continue

                fill_ratio = np.count_nonzero(roi_circle) / roi_circle.size
                if fill_ratio > best_fill:
                    best_fill  = fill_ratio
                    filled_opt = OPTIONS[oi]

            results[q_num] = filled_opt

    return results


# ---------------------------------------------------------------------------
# Função principal
# ---------------------------------------------------------------------------
def process_omr_pdf(
    pdf_bytes: bytes,
    db,
    expected_exam_id: Optional[int] = None,
) -> dict:
    """
    Processa um PDF escaneado com folhas OMR.
    Retorna resumo com páginas processadas, erros e answers salvos.
    """
    from app.models.exam import Exam, ExamQuestionLink
    from app.models.student_answer import StudentAnswer
    from app.models.school import Student

    images = _pdf_to_images(pdf_bytes)
    if not images:
        return {"error": "Não foi possível converter o PDF em imagens.", "pages": 0}

    summary = {"pages": len(images), "processed": 0, "errors": [], "answers_saved": 0}

    for page_idx, image in enumerate(images):
        try:
            # 1. Lê barcode
            barcode_str = _read_barcode(image)
            if not barcode_str:
                summary["errors"].append(f"Página {page_idx+1}: barcode não encontrado.")
                continue

            exam_id, student_id = _parse_barcode(barcode_str)
            if not exam_id or not student_id:
                summary["errors"].append(f"Página {page_idx+1}: barcode inválido ({barcode_str}).")
                continue

            if expected_exam_id and exam_id != expected_exam_id:
                summary["errors"].append(
                    f"Página {page_idx+1}: exam_id {exam_id} não corresponde ao esperado {expected_exam_id}."
                )
                continue

            # 2. Valida aluno e exam no banco
            exam    = db.get(Exam, exam_id)
            student = db.get(Student, student_id)
            if not exam or not student:
                summary["errors"].append(f"Página {page_idx+1}: exam ou aluno não encontrado.")
                continue

            # 3. Busca links com gabarito
            links = (
                db.query(ExamQuestionLink)
                .filter(ExamQuestionLink.exam_id == exam_id)
                .order_by(ExamQuestionLink.order_idx)
                .all()
            )
            n_questions = len(links)
            if not n_questions:
                summary["errors"].append(f"Página {page_idx+1}: nenhuma questão no exam.")
                continue

            # 4. Detecta bolhas
            thresh    = _preprocess(image)
            grid_rect = _find_bubble_grid(thresh)
            if not grid_rect:
                summary["errors"].append(f"Página {page_idx+1}: grid de bolhas não localizado.")
                continue

            filled = _detect_filled_bubbles(thresh, grid_rect, n_questions)

            # 5. Salva StudentAnswer (upsert)
            saved = 0
            for order_idx, link in enumerate(links):
                q_num        = order_idx + 1
                marked       = filled.get(q_num)
                correct      = link.correct_label
                is_correct   = (marked == correct) if (marked and correct) else None

                existing = (
                    db.query(StudentAnswer)
                    .filter_by(exam_id=exam_id, student_id=student_id, question_link_id=link.id)
                    .first()
                )
                if existing:
                    existing.marked_label = marked
                    existing.is_correct   = is_correct
                else:
                    db.add(StudentAnswer(
                        exam_id          = exam_id,
                        student_id       = student_id,
                        question_link_id = link.id,
                        marked_label     = marked,
                        is_correct       = is_correct,
                    ))
                saved += 1

            db.commit()
            summary["processed"]    += 1
            summary["answers_saved"] += saved
            log.info(f"[omr_scanner] exam={exam_id} student={student_id} → {saved} respostas salvas")

        except Exception as e:
            db.rollback()
            summary["errors"].append(f"Página {page_idx+1}: erro inesperado — {e}")
            log.exception(f"[omr_scanner] erro na página {page_idx+1}")

    return summary
