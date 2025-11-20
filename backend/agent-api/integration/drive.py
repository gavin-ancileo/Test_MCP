"""Google Drive API integration"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

async def upload_to_drive(file_data, filename, folder_id, credentials):
    """Upload document to Google Drive"""
    service = build('drive', 'v3', credentials=credentials)
    
    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }
    
    media = MediaFileUpload(file_data, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id,webViewLink'
    ).execute()
    
    return file.get('webViewLink')