import pickle
import os
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
import mimetypes
import argparse
from google.oauth2.credentials import Credentials
import socket
from tqdm import tqdm

SCOPES = ['https://www.googleapis.com/auth/drive']

credentials_json = 'auth/credentials.json'
credentials_pickle = 'auth/token.pickle'

# authentication and Drive API client
def get_drive_service():
    creds = None
    if os.path.exists(credentials_pickle):
        with open(credentials_pickle, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_json, SCOPES)
            creds = flow.run_local_server(port=0, launch_browser=True)
        with open(credentials_pickle, 'wb') as token:
            pickle.dump(creds, token)
    service = build('drive', 'v3', credentials=creds)
    return service

def upload_file_to_shared_drive(file_path, shared_folder_id):
    try:
        service = get_drive_service()
        file_name = os.path.basename(file_path)
        mime_type = mimetypes.guess_type(file_path)[0]
        file_metadata = {
            'name': file_name,
            'mimeType': mime_type,
            'parents': [shared_folder_id]
        }
        media = MediaFileUpload(file_path, mimetype=mime_type, chunksize=1024*1024, resumable=True)
        request = service.files().create(body=file_metadata, media_body=media, supportsAllDrives=True)
        file_size = os.path.getsize(file_path)
        pbar = tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024, desc=file_name)
        response = None
        previous_progress = 0
        while response is None:
            status, response = request.next_chunk()
            if status:
                current_progress = int(status.progress() * file_size)
                pbar.update(current_progress - previous_progress)
                previous_progress = current_progress
        pbar.close()
        file_id = response.get('id')
        file_url = f'"https://drive.google.com/u/0/uc?id={file_id}&export=download"'
        print(f"File download link: {file_url}")
        # Creates an anchorchain.txt file for use with the anchorchain plugin in Jenkins
        file_url = file_url.replace('"','')
        with open("anchorchain.txt", "w") as f:
            f.write(file_name + "\t" + file_url + "\thttps://cdn-icons-png.flaticon.com/512/2965/2965323.png")
    except HttpError as error:
        print(F'An error occurred: {error}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Uploads a file to a google shared drive')
    parser.add_argument('file_path', metavar='file_path', type=str,
                        help='path to the file to be uploaded')
    parser.add_argument('shared_folder_id', metavar='shared_folder_id', type=str,
                        help='id of the shared drive')
    args = parser.parse_args()

    upload_file_to_shared_drive(args.file_path, args.shared_folder_id)
