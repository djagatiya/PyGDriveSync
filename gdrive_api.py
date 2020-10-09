from __future__ import print_function

import hashlib
import io
import pickle
import os.path
import shutil

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive']

PAGE_SIZE = 1000
TOKEN_PICKLE = "token.pickle"
CREDENTIALS_JSON = "credentials.json"

CHUNK_SIZE = 1024 * 1024 * 5

VND_GOOGLE_APPS_FOLDER = 'application/vnd.google-apps.folder'

FILED_ID, FILED_NAME, FILED_MIME_TYPE, FILED_CHECKSUM, FILED_SIZE = 'id', 'name', 'mimeType', 'md5Checksum', 'size'


def get_service():
    creds = None
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_JSON, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials
        with open(TOKEN_PICKLE, 'wb') as token:
            pickle.dump(creds, token)
    service = build('drive', 'v3', credentials=creds)
    return service


def md5_checksum_file(file_name):
    md5_hash = hashlib.md5()
    with open(file_name, "rb") as f:
        chunk = f.read(4096 * 5)
        while len(chunk) > 0:
            md5_hash.update(chunk)
            chunk = f.read(4096 * 5)
    return md5_hash.hexdigest()


def file_dir_remove(path):
    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)
    else:
        raise ValueError(f"Given path is not dir/file. Path:{path}")


def get(file_id):
    service = get_service()
    data = service.files().get(fileId=file_id).execute()
    service.close()
    return data


def get_root():
    return get('root')


def files_list(q, selected_fields='id, name'):
    service = get_service()
    print(q, selected_fields)
    all_files = []
    next_page_token = None
    while True:
        print("Call...", next_page_token)
        print(q, selected_fields)
        result = service.files().list(
            q=q,
            pageSize=PAGE_SIZE,
            fields=f"nextPageToken, files({selected_fields})",
            pageToken=next_page_token
        ).execute()
        all_files.extend(result['files'])
        print(len(all_files))
        next_page_token = result.get('nextPageToken')
        if next_page_token is None:
            break
    print("Total files:", len(all_files))
    service.close()
    return all_files


def delete_local_files_and_folder(list_of_paths):
    for p in list_of_paths:
        file_dir_remove(p)


def download_file(file_id, dest_path, call_back):
    service = get_service()
    request = service.files().get_media(fileId=file_id)
    with io.FileIO(dest_path, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request, CHUNK_SIZE)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            call_back([file_id, dest_path, int(status.progress() * 100)])
    service.close()


def g_drive_to_local_sync(dir_file_id, dest_path, call_back):
    if not os.path.exists(dest_path):
        os.mkdir(dest_path)

    q = f"(not trashed) and ('{dir_file_id}' in parents)"
    selected_fields = "id, name, mimeType, size, md5Checksum"
    drive_file_list = files_list(q, selected_fields=selected_fields)

    drive_names = [f[FILED_NAME] for f in drive_file_list]
    local_list = os.listdir(dest_path)
    list_local_names = [i for i in local_list if i not in drive_names]

    paths = [os.path.join(dest_path, name) for name in list_local_names]
    print("Paths going to delete:", paths)
    yield delete_local_files_and_folder, (paths,)

    for f in drive_file_list:
        print(f)
        dest_abs_path = os.path.join(dest_path, f[FILED_NAME])
        if f[FILED_MIME_TYPE] == VND_GOOGLE_APPS_FOLDER:
            g_drive_to_local_sync(f[FILED_ID], dest_abs_path, call_back)
        else:
            if os.path.exists(dest_abs_path) and md5_checksum_file(dest_abs_path) == f[FILED_CHECKSUM]:
                print("File Checksum is same..")
                continue
            yield download_file, (f[FILED_ID], dest_abs_path, call_back)
