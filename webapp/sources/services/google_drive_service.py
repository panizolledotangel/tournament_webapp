import io
import json
import logging
import os
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from oauth2client.service_account import ServiceAccountCredentials


class GoogleDriveService:

    @classmethod
    def convert_to_date(cls, date_str):
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    
    def __init__(self):
        self.logger = logging.getLogger("acotournament")
        self._SCOPES=['https://www.googleapis.com/auth/drive']
        self.service = None
        self.build()

    def build(self):
        creds = ServiceAccountCredentials.from_json_keyfile_name(os.getenv("GOOGLE_CREDENTIALS_PATH"), self._SCOPES)
        self.service = build('drive', 'v3', credentials=creds)
    
    def list_files(self, folder_id = None):
        query = f"'{folder_id}' in parents and trashed=false" if folder_id else "trashed=false"
        
        selected_fields = "files(id,name,mimeType,md5Checksum,modifiedTime)"
        
        list_file = self.service.files().list(q=query, fields=selected_fields).execute()
        return list_file["files"]
    
    def load_json(self, file_id):
        self.logger.debug(f"Downloading file {file_id}")

        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while done is False:
            status, done = downloader.next_chunk()
            self.logger.debug(f"Download {int(status.progress() * 100)}")

        fh.seek(0)
        return json.load(fh)