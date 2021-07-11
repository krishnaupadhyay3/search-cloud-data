from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload
import json
import io
import os
import random
import string
from .database import redisClient
from rq import Queue
from .extractor_worker import extract_data


fileQueue = Queue('tikaExtractor', connection=redisClient)
with open("./workers/client_secret.json") as fp:
    credz = json.load(fp)
credentials = service_account.Credentials.from_service_account_info(credz)
drive_service = build('drive', 'v3', credentials=credentials)


def get_file_id(file_url):
    ''' extract the file id from google drive share url
        params : google drive share url
        return : file id
    '''
    return file_url.split("/")[5]


def get_file_name_from_drive(drive_service, file_id):
    ''' return the file_name from the google drive api call
        params : file_id
        return : str(file_name)
    '''
    file_info = drive_service.files().get(fileId=file_id).execute()
    return file_info["name"]


def get_available_file_name(file_name, folder):
    while os.path.isfile(folder+file_name):
        name, ext = os.path.splitext(file_name)
        es = ''.join(random.choices(string.ascii_uppercase +
                                    string.digits, k=7))
        file_name = name + es + ext
    return folder+file_name


def download_file(drive_service, file_id, file_name):

    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))


def download_google_file(file_url):
    try:
        file_id = get_file_id(file_url)
        file_name = get_file_name_from_drive(drive_service, file_id)
        download_folder = os.getenv("DOWNLOAD_FOLDER", "./data/")
        file_name = get_available_file_name(file_name, download_folder)
        download_file(drive_service, file_id, file_name)
        redisClient.hmset(file_id, {"status": "success"})
        fileQueue.enqueue_call(func=extract_data,
                               args=(file_name, file_id,), job_id=file_id)

    except Exception as ex:
        redisClient.hmset(file_id, {"status": "failed", "error": str(ex)})
