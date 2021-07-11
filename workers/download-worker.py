from googleapiclient.discovery import build
from google.oauth2 import service_account
import json

credz = json.loads("workers/client_secret.json")
credentials = service_account.Credentials.from_service_account_info(credz)
drive_service = build('drive', 'v3', credentials=credentials)

def get_file_id(file_url):
	''' extract the file id from google drive share url
		params : google drive share url
		return : file id
    '''

	return file_url.split("/")[5]

def get_file_name_from_drive(drive_service,file_id):
	''' return the file_name from the google drive api call
		params : file_id
		return : str(file_name)
	'''
	file_info = drive_service.files().get(fileId=file_id).execute()
	return file_info["name"]