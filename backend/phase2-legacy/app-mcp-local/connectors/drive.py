import json
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

class DriveConnector:
    def __init__(self):
        creds_path = Path(__file__).parent / "drive_credentials.json"

        if creds_path.exists():
            with open(creds_path, "r", encoding="utf-8") as f:
                creds_json = json.load(f)   # parse thành dict

            self.creds = service_account.Credentials.from_service_account_info(
                creds_json,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            self.service = build('drive', 'v3', credentials=self.creds)
        else:
            self.service = None
            print("❌ No Drive credentials found")

    def upload_text(self, content, filename, folder_id=None):
        if not self.service:
            return None

        file_metadata = {
            'name': filename,
            'mimeType': 'application/vnd.google-apps.document'
        }

        if folder_id:
            # Extract folder ID from drive://folder/xxx format
            if folder_id.startswith('drive://folder/'):
                folder_id = folder_id.replace('drive://folder/', '')
            file_metadata['parents'] = [folder_id]

        media = MediaIoBaseUpload(
            io.BytesIO(content.encode('utf-8')),
            mimetype='text/plain',
            resumable=True
        )

        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink',
            supportsAllDrives=True   # 👈 thêm dòng này
        ).execute()

        return file.get('webViewLink')
    
    def upload_docx(self, file_bytes, filename, folder_id):
        file_metadata = {"name": filename, "parents": [folder_id]}
        media = MediaIoBaseUpload(
            io.BytesIO(file_bytes),
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            resumable=True
        )
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id,webViewLink",
            supportsAllDrives=True
        ).execute()
        return file.get("webViewLink")

