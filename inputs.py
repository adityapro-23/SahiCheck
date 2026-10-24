"""Step 0: Deterministic Input Normalizer (inputs.py).
Converts uploaded image/PDF or pasted text into a single NormalizedInput object.
Uses pypdfium2 to render PDF pages to images and pypdf to read any exact text layer.
"""

import io
import os
from typing import List, Optional

from PIL import Image
import pypdf
import pypdfium2 as pdfium

from schemas import NormalizedInput

MAX_TEXT_CHARS = 15000
MAX_IMAGE_DIMENSION = 1600
MAX_FILE_BYTES = 15 * 1024 * 1024  # 15 MB
MAX_PDF_PAGES = 2
ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def _downscale_and_encode_png(pil_img: Image.Image) -> bytes:
    """Converts PIL Image to RGB, downscales if larger than MAX_IMAGE_DIMENSION, and returns PNG bytes."""
    if pil_img.mode not in ("RGB", "L"):
        pil_img = pil_img.convert("RGB")
    width, height = pil_img.size
    if max(width, height) > MAX_IMAGE_DIMENSION:
        scale = MAX_IMAGE_DIMENSION / float(max(width, height))
        new_size = (max(1, int(width * scale)), max(1, int(height * scale)))
        pil_img = pil_img.resize(new_size, Image.Resampling.LANCZOS)

    buf = io.BytesIO()
    pil_img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def _process_pdf_bytes(raw: bytes) -> tuple[List[bytes], Optional[str], List[str]]:
    """Same as _process_pdf but accepts raw bytes so nothing is written to disk."""
    warnings: List[str] = []
    rendered_images: List[bytes] = []
    pdf_text_parts: List[str] = []

    # 1. Text layer via pypdf (from a BytesIO stream)
    try:
        reader = pypdf.PdfReader(io.BytesIO(raw))
        if len(reader.pages) > MAX_PDF_PAGES:
            warnings.append(f"PDF has {len(reader.pages)} pages; analyzing the first {MAX_PDF_PAGES} pages.")
        for page in reader.pages[:MAX_PDF_PAGES]:
            extracted = (page.extract_text() or "").strip()
            if extracted:
                pdf_text_parts.append(extracted)
    except Exception as exc:
        warnings.append(f"Could not read PDF text layer with pypdf: {exc}")

    # 2. Render pages to PNG images with pypdfium2 (accepts bytes directly)
    try:
        pdf_doc = pdfium.PdfDocument(raw)
        page_count = len(pdf_doc)
        for idx in range(min(page_count, MAX_PDF_PAGES)):
            page = pdf_doc[idx]
            bitmap = page.render(scale=2.0)
            pil_img = bitmap.to_pil()
            rendered_images.append(_downscale_and_encode_png(pil_img))
            page.close()
        pdf_doc.close()
    except Exception as exc:
        raise ValueError(f"Failed to render PDF pages with pypdfium2: {exc}") from exc

    pdf_text_layer = "\n\n".join(pdf_text_parts).strip() if pdf_text_parts else None
    if pdf_text_layer and len(pdf_text_layer) > MAX_TEXT_CHARS:
        pdf_text_layer = pdf_text_layer[:MAX_TEXT_CHARS]
        warnings.append(f"PDF text layer truncated to {MAX_TEXT_CHARS} characters.")

    return rendered_images, pdf_text_layer, warnings


def _process_pdf(file_path: str) -> tuple[List[bytes], Optional[str], List[str]]:
    """Renders up to MAX_PDF_PAGES with pypdfium2 and extracts text layer with pypdf."""
    warnings: List[str] = []
    rendered_images: List[bytes] = []
    pdf_text_parts: List[str] = []

    # 1. Extract exact text layer with pypdf
    try:
        reader = pypdf.PdfReader(file_path)
        if len(reader.pages) > MAX_PDF_PAGES:
            warnings.append(f"PDF has {len(reader.pages)} pages; analyzing the first {MAX_PDF_PAGES} pages.")
        for page in reader.pages[:MAX_PDF_PAGES]:
            extracted = (page.extract_text() or "").strip()
            if extracted:
                pdf_text_parts.append(extracted)
    except Exception as exc:
        warnings.append(f"Could not read PDF text layer with pypdf: {exc}")

    # 2. Render pages to PNG images with pypdfium2
    try:
        pdf_doc = pdfium.PdfDocument(file_path)
        page_count = len(pdf_doc)
        for idx in range(min(page_count, MAX_PDF_PAGES)):
            page = pdf_doc[idx]
            bitmap = page.render(scale=2.0)
            pil_img = bitmap.to_pil()
            rendered_images.append(_downscale_and_encode_png(pil_img))
            page.close()
        pdf_doc.close()
    except Exception as exc:
        raise ValueError(f"Failed to render PDF pages with pypdfium2: {exc}") from exc

    pdf_text_layer = "\n\n".join(pdf_text_parts).strip() if pdf_text_parts else None
    if pdf_text_layer and len(pdf_text_layer) > MAX_TEXT_CHARS:
        pdf_text_layer = pdf_text_layer[:MAX_TEXT_CHARS]
        warnings.append(f"PDF text layer truncated to {MAX_TEXT_CHARS} characters.")

    return rendered_images, pdf_text_layer, warnings


def normalize_input(
    file_path: Optional[str] = None,
    pasted_text: Optional[str] = None,
    # New in-memory path: pass raw bytes + extension instead of a disk path.
    file_bytes: Optional[bytes] = None,
    file_suffix: Optional[str] = None,
) -> NormalizedInput:
    """Validates and normalizes either an uploaded Image/PDF or pasted text.

    Accepts input in two forms:
      1. file_path (str) – legacy path to a temp file on disk.
      2. file_bytes (bytes) + file_suffix (str) – in-memory bytes (no disk writes).
    """
    clean_text = (pasted_text or "").strip()
    has_file = bool(file_path and str(file_path).strip()) or bool(file_bytes and file_suffix)

    if not has_file and not clean_text:
        raise ValueError(
            "Please provide either an offer letter screenshot/PDF or paste the suspicious job message."
        )

    warnings: List[str] = []
    if clean_text and len(clean_text) > MAX_TEXT_CHARS:
        clean_text = clean_text[:MAX_TEXT_CHARS]
        warnings.append(f"Pasted text was truncated to {MAX_TEXT_CHARS} characters.")

    # --- In-memory file path (new) ---
    if file_bytes is not None and file_suffix:
        ext = file_suffix.lower()
        if len(file_bytes) == 0:
            raise ValueError("Uploaded file is empty (0 bytes).")
        if len(file_bytes) > MAX_FILE_BYTES:
            raise ValueError("Uploaded file exceeds the 15 MB size limit.")
        if ext == ".pdf":
            images, pdf_text_layer, pdf_warnings = _process_pdf_bytes(file_bytes)
            warnings.extend(pdf_warnings)
            return NormalizedInput(
                input_type="image",
                images=images,
                text=clean_text if clean_text else None,
                pdf_text_layer=pdf_text_layer,
                warnings=warnings,
            )
        elif ext in ALLOWED_IMAGE_EXTS:
            try:
                with Image.open(io.BytesIO(file_bytes)) as img:
                    png_bytes = _downscale_and_encode_png(img)
            except Exception as exc:
                raise ValueError(f"Could not read uploaded image: {exc}") from exc
            return NormalizedInput(
                input_type="image",
                images=[png_bytes],
                text=clean_text if clean_text else None,
                pdf_text_layer=None,
                warnings=warnings,
            )
        else:
            raise ValueError(
                f"Unsupported file type '{ext}'. Please upload a PNG, JPG image or a PDF file."
            )

    # --- Legacy disk-path ---

    # --- Legacy disk-path ---
    if has_file:
        path_str = str(file_path)
        if not os.path.exists(path_str):
            raise ValueError("Uploaded file could not be found.")
        file_size = os.path.getsize(path_str)
        if file_size == 0:
            raise ValueError("Uploaded file is empty (0 bytes).")
        if file_size > MAX_FILE_BYTES:
            raise ValueError("Uploaded file exceeds the 15 MB size limit.")

        ext = os.path.splitext(path_str)[1].lower()
        if ext == ".pdf":
            images, pdf_text_layer, pdf_warnings = _process_pdf(path_str)
            warnings.extend(pdf_warnings)
            return NormalizedInput(
                input_type="image",
                images=images,
                text=clean_text if clean_text else None,
                pdf_text_layer=pdf_text_layer,
                warnings=warnings,
            )
        elif ext in ALLOWED_IMAGE_EXTS:
            try:
                with Image.open(path_str) as img:
                    png_bytes = _downscale_and_encode_png(img)
            except Exception as exc:
                raise ValueError(f"Could not read uploaded image: {exc}") from exc

            return NormalizedInput(
                input_type="image",
                images=[png_bytes],
                text=clean_text if clean_text else None,
                pdf_text_layer=None,
                warnings=warnings,
            )
        else:
            raise ValueError(
                f"Unsupported file type '{ext}'. Please upload a PNG, JPG, WEBP image or a PDF file."
            )

    # Pure text mode
    return NormalizedInput(
        input_type="text",
        images=[],
        text=clean_text,
        pdf_text_layer=None,
        warnings=warnings,
    )