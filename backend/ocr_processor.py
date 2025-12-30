"""
OCR processor based on Microsoft TrOCR.
Fallback for cases where the external parser fails or returns empty data.
"""
from __future__ import annotations

import io
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import fitz  # PyMuPDF
from PIL import Image, ImageOps


class OCRProcessor:
    """Processes scanned PDFs through Microsoft TrOCR."""

    def __init__(self) -> None:
        self.model = None
        self.processor = None
        self.device = None
        self._initialized = False

    def _initialize_model(self) -> None:
        """Lazy-load the TrOCR model on first use."""
        if self._initialized:
            return

        try:
            print("[OCR] Initialising Microsoft TrOCR model...")
            print("[OCR] First run may take a few minutes while weights download")

            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
            import torch

            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"[OCR] Device: {self.device.upper()}")

            model_name = "microsoft/trocr-base-printed"
            print(f"[OCR] Loading model: {model_name}")

            self.processor = TrOCRProcessor.from_pretrained(model_name)
            self.model = VisionEncoderDecoderModel.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()

            self._initialized = True
            print("[OCR] Model ready")

        except ImportError as exc:
            print("[OCR] Missing dependencies: install transformers torch pillow")
            raise Exception("OCR dependencies are not installed") from exc

        except Exception as exc:  # pylint: disable=broad-except
            print(f"[OCR] Error initialising TrOCR: {exc}")
            raise

    def extract_text_from_pdf(self, pdf_path: str) -> Dict:
        """Extract text (and coarse layout data) from a PDF using OCR."""
        self._initialize_model()

        print("\n[OCR] " + "=" * 60)
        print(f"[OCR] Processing PDF with OCR: {Path(pdf_path).name}")
        print("[OCR] " + "=" * 60)

        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        print(f"[OCR] Total pages: {total_pages}")

        pages: List[Dict] = []

        try:
            for page_index in range(total_pages):
                print(f"\n[OCR] Page {page_index + 1}/{total_pages}")
                page = doc[page_index]

                page_text, line_items = self._extract_text_from_page(page)

                pages.append(
                    {
                        "text": page_text,
                        "page_number": page_index + 1,
                        "lines": line_items,
                    }
                )

                print(f"[OCR] Characters extracted: {len(page_text)}")

        finally:
            doc.close()

        print("\n[OCR] " + "=" * 60)
        print(f"[OCR] OCR finished: {total_pages} page(s)")
        print("[OCR] " + "=" * 60 + "\n")

        return {"pages": pages}

    def _extract_text_from_page(self, page: fitz.Page) -> Tuple[str, List[Dict]]:
        """Perform OCR over a single page and collect coarse bounding boxes."""
        import torch

        zoom = 2.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)

        image = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        print(f"[OCR]   Page rasterised at {image.size[0]}x{image.size[1]} px")

        line_items = self._extract_text_lines_from_image(page, image, zoom)
        page_text = "\n".join(item["text"] for item in line_items)

        return page_text, line_items

    def _extract_text_lines_from_image(
        self,
        page: fitz.Page,
        image: Image.Image,
        zoom: float,
    ) -> List[Dict]:
        """Extract text in horizontal stripes, returning coarse bounding boxes."""
        import torch

        width, height = image.size
        stripe_height = 100
        num_stripes = max(1, height // stripe_height)

        print(f"[OCR]   Processing {num_stripes} stripe(s) of text...")

        lines: List[Dict] = []
        page_width = page.rect.width
        page_height = page.rect.height

        for index in range(num_stripes):
            y_start = index * stripe_height
            y_end = min((index + 1) * stripe_height, height)
            stripe = image.crop((0, y_start, width, y_end))

            try:
                pixel_values = self.processor(stripe, return_tensors="pt").pixel_values
                pixel_values = pixel_values.to(self.device)

                with torch.no_grad():
                    generated_ids = self.model.generate(pixel_values)

                generated_text = self.processor.batch_decode(
                    generated_ids, skip_special_tokens=True
                )[0]

                cleaned = generated_text.strip()
                if not cleaned:
                    continue

                stripe_gray = stripe.convert("L")
                inverted = ImageOps.invert(stripe_gray)
                binary = inverted.point(lambda p: 255 if p > 20 else 0)
                bbox_pixels = binary.getbbox()

                if not bbox_pixels:
                    bbox_pixels = (0, 0, stripe.width, stripe.height)

                left_px, top_px, right_px, bottom_px = bbox_pixels

                x0_pdf = max(0.0, left_px / zoom)
                x1_pdf = min(page_width, right_px / zoom)
                y0_pdf = max(0.0, (y_start + top_px) / zoom)
                y1_pdf = min(page_height, (y_start + bottom_px) / zoom)

                text_length = len(cleaned)
                char_width = (x1_pdf - x0_pdf) / text_length if text_length else (x1_pdf - x0_pdf)

                lines.append(
                    {
                        "text": cleaned,
                        "bbox": [x0_pdf, y0_pdf, x1_pdf, y1_pdf],
                        "stripe_index": index,
                        "text_length": text_length,
                        "char_width": char_width,
                        "x0": x0_pdf,
                        "y0": y0_pdf,
                    }
                )

            except Exception as exc:  # pylint: disable=broad-except
                print(f"[OCR]   Stripe {index + 1} failed: {exc}")
                continue

        print(f"[OCR]   Extracted {len(lines)} stripe(s) with text")
        return lines

    def can_use_ocr(self) -> bool:
        """Return True when all OCR dependencies are importable."""
        try:
            import transformers  # noqa: F401
            import torch  # noqa: F401
            from PIL import Image  # noqa: F401

            return True
        except ImportError:
            return False


# Global instance used across the backend
ocr_processor = OCRProcessor()
