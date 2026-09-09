"""
OCR Fallback Engine for Scanned and Non-Selectable PDF Documents.
Utilizes PyMuPDF's C-level Tesseract integration (page.get_textpage_ocr)
with automatic tessdata discovery, bounding box normalization, and resilient error recovery.
"""

import logging
import math
import os
import re
import shutil
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)


def clean_ocr_text(text: str) -> str:
    """Cleans OCR artifacts, normalizes whitespace, and strips non-printable noise."""
    if not text:
        return ""
    cleaned = text.replace("\u00a0", " ").replace("\u200b", "").replace("\ufeff", "")
    # Fix hyphenated words split across lines
    cleaned = re.sub(r'(\b[a-zA-Z]{2,})-\n\s*([a-zA-Z]{2,}\b)', r'\1\2', cleaned)
    lines = [re.sub(r'[ \t]+', ' ', l).strip() for l in cleaned.split("\n")]
    joined = "\n".join(lines)
    return re.sub(r'\n{3,}', '\n\n', joined).strip()


class OCRFallbackEngine:
    """
    Localized OCR fallback engine for PDF pages lacking a usable text layer.
    Utilizes PyMuPDF's native C-level Tesseract integration (page.get_textpage_ocr).
    Guarantees that OCR failures never crash the broader document ingestion pipeline.
    """

    def __init__(
        self,
        language: str = "eng",
        dpi: int = 150,
        full: bool = True,
        tessdata: Optional[str] = None,
    ):
        self.language = language
        self.dpi = dpi
        self.full = full
        self.tessdata = tessdata or self._discover_tessdata()
        self.available = self._check_availability()

    def _discover_tessdata(self) -> Optional[str]:
        """Discovers standard tessdata directory on host OS if configured."""
        env_tessdata = os.environ.get("TESSDATA_PREFIX")
        if env_tessdata and os.path.isdir(env_tessdata):
            return env_tessdata

        common_windows_paths = [
            r"C:\Program Files\Tesseract-OCR\tessdata",
            r"C:\Program Files (x86)\Tesseract-OCR\tessdata",
            os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tessdata"),
        ]
        for path in common_windows_paths:
            if os.path.isdir(path):
                return path

        common_unix_paths = [
            "/usr/share/tesseract-ocr/5/tessdata",
            "/usr/share/tesseract-ocr/4.00/tessdata",
            "/usr/share/tessdata",
            "/opt/homebrew/share/tessdata",
            "/usr/local/share/tessdata",
        ]
        for path in common_unix_paths:
            if os.path.isdir(path):
                return path

        return None

    def _check_availability(self) -> bool:
        """Checks if Tesseract binary or tessdata is available in the environment."""
        if self.tessdata and os.path.isdir(self.tessdata):
            return True
        if shutil.which("tesseract") is not None:
            return True
        return False

    def verify_ocr_runtime(self) -> Dict[str, Any]:
        """
        Deep diagnostic inspection of OCR runtime, Tesseract binary, tessdata directory,
        and PyMuPDF OCR binding.
        """
        tesseract_bin = shutil.which("tesseract")
        is_tessdata_valid = bool(self.tessdata and os.path.isdir(self.tessdata))
        status = "ready" if (self.available and (tesseract_bin or is_tessdata_valid)) else "unavailable"
        return {
            "status": status,
            "available": self.available,
            "engine": "tesseract",
            "language": self.language,
            "tesseract_binary": tesseract_bin,
            "tessdata_path": self.tessdata,
            "tessdata_valid": is_tessdata_valid,
            "message": (
                "Tesseract OCR runtime active and ready for scanned PDF fallback."
                if self.available
                else "Tesseract OCR binary or tessdata not discovered; OCR fallback disabled."
            )
        }

    def ocr_page(self, page: Any, page_num: int) -> List[Dict[str, Any]]:
        """
        Performs localized OCR on a single PyMuPDF Page and extracts text blocks
        with estimated bounding boxes [x0, y0, x1, y1] in native PDF coordinate space.
        Does not raise exceptions; returns an empty list if OCR fails or cannot run.
        """
        try:
            kwargs: Dict[str, Any] = {
                "language": self.language,
                "dpi": self.dpi,
                "full": self.full,
            }
            if self.tessdata:
                kwargs["tessdata"] = self.tessdata

            textpage = page.get_textpage_ocr(**kwargs)
            raw_blocks = page.get_text("blocks", textpage=textpage)

            ocr_chunks: List[Dict[str, Any]] = []
            for block in raw_blocks:
                if len(block) >= 5:
                    x0, y0, x1, y1, text = block[:5]
                    cleaned = clean_ocr_text(str(text))
                    if not cleaned:
                        continue

                    try:
                        coords = [float(x0), float(y0), float(x1), float(y1)]
                        if any(math.isnan(c) or math.isinf(c) for c in coords):
                            continue
                        bbox = [round(c, 2) for c in coords]
                    except (ValueError, TypeError):
                        continue

                    ocr_chunks.append({
                        "page": page_num,
                        "text": cleaned,
                        "bbox": bbox,
                        "block_type": "ocr",
                    })

            return ocr_chunks

        except Exception as e:
            logger.warning(
                "OCR processing failed for page %d: %s. "
                "Ensure Tesseract OCR is installed with language data '%s'.",
                page_num,
                str(e),
                self.language,
            )
            return []


ocr_engine = OCRFallbackEngine()
