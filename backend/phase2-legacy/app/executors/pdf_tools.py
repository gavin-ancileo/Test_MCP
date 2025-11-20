# app/executors/pdf_tools.py
from typing import Dict, Any
import io, logging

log = logging.getLogger(__name__)

def _try_pypdf_fill(pdf_bytes: bytes, values: Dict[str, Any]) -> bytes | None:
    try:
        from pypdf import PdfReader, PdfWriter
        from pypdf.generic import DictionaryObject, BooleanObject
    except Exception:
        return None
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        # gán field values cho từng trang (best-effort)
        for page in writer.pages:
            try:
                writer.update_page_form_field_values(page, values)
            except Exception:
                pass
        # đảm bảo appearance
        if "/AcroForm" in writer._root_object:
            writer._root_object["/AcroForm"].update({"/NeedAppearances": BooleanObject(True)})
        else:
            writer._root_object.update({
                "/AcroForm": DictionaryObject({"/NeedAppearances": BooleanObject(True)})
            })
        out = io.BytesIO()
        writer.write(out)
        out.seek(0)
        return out.read()
    except Exception as e:
        log.warning("pypdf fill failed: %s", e)
        return None

def fill_pdf_acroform(pdf_bytes: bytes, values: Dict[str, Any]) -> bytes:
    """
    Điền AcroForm nếu có pypdf; nếu không, trả lại bytes gốc (để không chặn demo).
    """
    filled = _try_pypdf_fill(pdf_bytes, values)
    if filled is None:
        log.warning("pypdf not installed/failed; return original PDF (no fields filled).")
        return pdf_bytes
    return filled

def fill_pdf_by_labels(pdf_bytes: bytes, label_map: Dict[str, str], values: Dict[str, Any]) -> bytes:
    """
    label_map: {"Candidate Name": "Text1", ...}
    values:   {"candidate_name":"...", "Text1":"..."} – ưu tiên field name; fallback từ label (normalize).
    """
    payload = {}

    # Map từ label → field (ưu tiên field name nếu đã có trong values)
    for label, field in (label_map or {}).items():
        v = values.get(field)
        if v is None:
            norm = label.lower().replace(" ", "_")
            v = values.get(norm)
        if v is not None:
            payload[field] = v

    # Merge thêm mọi cặp key/value “giống field name”
    for k, v in (values or {}).items():
        if isinstance(v, (str, int, float)) and k not in payload:
            payload[k] = v

    return fill_pdf_acroform(pdf_bytes, payload)
