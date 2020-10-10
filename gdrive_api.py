from __future__ import print_function

import hashlib
import io
import pickle
import os.path
import shutil

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

import logging

# Note: Remove some warning level logs.
googleapiclient_logger = logging.getLogger('googleapiclient.discovery_cache')
googleapiclient_logger.setLevel(logging.ERROR)

SCOPES = ['https://www.googleapis.com/auth/drive']

PAGE_SIZE = 1000
TOKEN_PICKLE = "token.pickle"
CLIENT_SECRETS_JSON = "client_secrets.json"

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
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_JSON, SCOPES)
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
    logging.debug(f"List of files: {q}, {selected_fields}")
    all_files = []
    next_page_token = None
    while True:
        logging.debug(f"Next Call...{next_page_token}")
        result = service.files().list(
            q=q,
            pageSize=PAGE_SIZE,
            fields=f"nextPageToken, files({selected_fields})",
            pageToken=next_page_token
        ).execute()
        all_files.extend(result['files'])
        logging.debug(f"Files of current page:{len(all_files)}")
        next_page_token = result.get('nextPageToken')
        if next_page_token is None:
            break
    logging.debug(f"Total files: {len(all_files)}")
    service.close()
    return all_files


def drive_trash_by_file_id(file_id):
    service = get_service()
    service.files().update(fileId=file_id, body={"trashed": True}).execute()
    service.close()


def make_drive_folder(name, parent_id):
    service = get_service()
    folder_id = service.files().create(
        body={'name': name,
              'parents': [parent_id],
              'mimeType': VND_GOOGLE_APPS_FOLDER},
        fields='id').execute()
    service.close()
    return folder_id


def delete_local_files_and_folder(list_of_paths):
    for p in list_of_paths:
        file_dir_remove(p)


def update_file(source_path, file_id):
    logging.info(f"Updating file:{source_path}, {file_id}")
    service = get_service()
    media = MediaFileUpload(source_path)
    service.files().update(fileId=file_id,
                           media_body=media,
                           fields='id').execute()
    service.close()


# todo: write method for Resumable upload
def upload_file(source_path, parent_id):
    service = get_service()
    file_metadata = {'name': os.path.basename(source_path), 'parents': [parent_id]}
    logging.info(f"Uploading file: {source_path}, {file_metadata}")
    media = MediaFileUpload(source_path)
    service.files().create(body=file_metadata,
                           media_body=media,
                           fields='id').execute()
    service.close()


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


def up_sync(source_path, drive_id, task_list: list):
    logging.info(f" >>>> UP-sync starting, {source_path}, {drive_id}")

    q = f"(not trashed) and ('{drive_id}' in parents)"
    selected_fields = "id, name, mimeType, size, md5Checksum"
    drive_file_list = files_list(q, selected_fields=selected_fields)

    logging.debug(f"drive_file_list: {len(drive_file_list)}")
    drive_dict = {d[FILED_NAME]: d for d in drive_file_list}

    local_list = os.listdir(source_path)
    logging.debug(f"local_list:{len(local_list)}")

    # delete if contain only on drive
    for name, d in drive_dict.items():
        if name not in local_list:
            logging.info(f"Trashing file/folder:, {d}")
            task_list.append((drive_trash_by_file_id, (d[FILED_ID],)))

    logging.info("Traversing Local files...")
    for local_name in local_list:

        logging.info(f"Local file name: {local_name}")
        drive_data = drive_dict.get(local_name)
        local_abs = os.path.join(source_path, local_name)

        # there is no files/folder
        if drive_data is None:
            if os.path.isfile(local_abs):
                logging.info(f"\t-Upload_file")
                task_list.append((upload_file, (local_abs, drive_id)))
            elif os.path.isdir(local_abs):
                logging.info(f"\t-create directory")
                created_drive_id = make_drive_folder(local_name, drive_id)
                up_sync(local_abs, created_drive_id[FILED_ID], task_list)
            else:
                raise Exception("This is not file/Directory.")
        else:
            logging.info(f"\t-Drive data item:{drive_data}")
            drive_data_id = drive_data[FILED_ID]
            if drive_data[FILED_MIME_TYPE] == VND_GOOGLE_APPS_FOLDER:
                logging.info("\t-Traversing sub directory.")
                up_sync(local_abs, drive_data_id, task_list)
            else:
                # zero byte file
                file_size = drive_data.get(FILED_SIZE)
                if file_size is None:
                    logging.info("\t-Empty file removed.")
                    drive_trash_by_file_id(drive_data_id)
                    logging.info("\t-It will be updated new-one.")
                    task_list.append((upload_file, (local_abs, drive_id)))
                    continue

                # skip if check-sum is same
                check_sum = drive_data.get(FILED_CHECKSUM)
                if check_sum is not None and md5_checksum_file(local_abs) == check_sum:
                    logging.info("\t-Checksum is same.")
                    continue

                logging.info(f"\t-Update file.")
                task_list.append((update_file, (local_abs, drive_data_id)))


def down_sync(file_id, dest_path, task_list: list, call_back):
    logging.info(f" >>>> DOWN-Sync Started: {file_id}, {dest_path}")

    if not os.path.exists(dest_path):
        os.mkdir(dest_path)
        logging.info(f"\t-Directory created:{dest_path}")

    # list google-drive files/folders.
    drive_list = files_list(
        f"(not trashed) and ('{file_id}' in parents)"
        , selected_fields="id, name, mimeType, size, md5Checksum")

    # delete local file system files and folder.
    drive_list_names = [_item[FILED_NAME] for _item in drive_list]
    local_paths_to_delete = [os.path.join(dest_path, _name)
                             for _name in os.listdir(dest_path) if _name not in drive_list_names]
    if len(local_paths_to_delete) > 0:
        logging.info(f"Delete files and folder task added: {local_paths_to_delete}")
        # todo: support for move to recycle-bin
        task_list.append((delete_local_files_and_folder, (local_paths_to_delete,)))

    # traversing google drive files/folders.
    logging.info("Traversing Google drive....")
    for _item in drive_list:
        logging.info(f"\t-{_item}")
        _item_id = _item[FILED_ID]
        abs_path = os.path.join(dest_path, _item[FILED_NAME])
        if _item[FILED_MIME_TYPE] == VND_GOOGLE_APPS_FOLDER:
            # traversing sub-directory.
            logging.info("\t-Traversing sub directory.")
            down_sync(_item_id, abs_path, task_list, call_back)
        else:
            # zero bytes file
            file_size = _item.get("size")
            if file_size is None:
                logging.info("\t-Empty file created..")
                open(abs_path, 'w').close()
                continue

            # skip the download if checksum is equals.
            if os.path.exists(abs_path):
                check_sum = _item.get(FILED_CHECKSUM)
                if check_sum is not None and md5_checksum_file(abs_path) == check_sum:
                    logging.info("\t-File Checksum is same..")
                    continue

            # download file to local.
            task_list.append((download_file, (_item_id, abs_path, call_back)))
            logging.info("\t-Download_file task added")
