import os, io, json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
GDRIVE_IMPERSONATE_EMAIL = os.getenv("GDRIVE_IMPERSONATE_EMAIL")
_SCOPES = ["https://www.googleapis.com/auth/drive"]

def _svc():
    if not GOOGLE_SERVICE_ACCOUNT_JSON:
        raise RuntimeError("Missing GOOGLE_SERVICE_ACCOUNT_JSON")
    info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
    creds = service_account.Credentials.from_service_account_info(info, scopes=_SCOPES)
    if GDRIVE_IMPERSONATE_EMAIL:
        creds = creds.with_subject(GDRIVE_IMPERSONATE_EMAIL)
    return build("drive", "v3", credentials=creds, cache_discovery=False)

def _drive(): return _svc()

def _dl_bytes(file_id: str) -> bytes:
    svc = _drive()
    data = svc.files().get_media(fileId=file_id).execute()
    return data if isinstance(data, (bytes, bytearray)) else bytes(data)

def _download_text(file_id: str) -> str:
    return _dl_bytes(file_id).decode("utf-8")

def upload_bytes_to_drive(parent_folder_id: str, name: str, data: bytes, mime: str) -> str:
    svc = _drive()
    meta = {"name": name, "parents": [parent_folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(data), mimetype=mime, resumable=True)
    f = svc.files().create(body=meta, media_body=media, fields="id").execute()
    return f["id"]

def convert_docx_to_google_doc(file_id: str) -> str:
    svc = _drive()
    gdoc = svc.files().copy(
        fileId=file_id,
        body={"mimeType":"application/vnd.google-apps.document"},
        fields="id"
    ).execute()
    return gdoc["id"]

def export_google_doc_to_pdf_bytes(gdoc_id: str) -> bytes:
    svc = _drive()
    pdf = svc.files().export(fileId=gdoc_id, mimeType="application/pdf").execute()
    return pdf if isinstance(pdf, (bytes, bytearray)) else bytes(pdf)
