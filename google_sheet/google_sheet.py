# 🔐 OAuth 인증 및 token.pickle 저장/불러오기
import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def get_gdrive_service():
  SCOPES = ['https://www.googleapis.com/auth/drive.file']
  creds = None

  # 현재 파일 기준으로 절대경로 생성
  base_dir = os.path.dirname(os.path.abspath(__file__))
  client_secret_path = os.path.join(base_dir, '../secret/client_secret.json')
  token_path = os.path.join(base_dir, '../secret/token.pickle')

  # 토큰 파일이 있으면 불러오기
  if os.path.exists(token_path):
    with open(token_path, 'rb') as token:
      creds = pickle.load(token)

  # 없거나 만료되었으면 새로 인증
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(client_secret_path,
                                                       SCOPES)
      creds = flow.run_local_server(port=0)
    # 토큰 저장
    with open(token_path, 'wb') as token:
      pickle.dump(creds, token)

  return build('drive', 'v3', credentials=creds)


def upload_and_convert_to_gsheet(local_file_path, gdrive_folder_id=None):
  service = get_gdrive_service()

  file_metadata = {
    'name': os.path.splitext(os.path.basename(local_file_path))[0],
    # 이름에서 .csv/.xlsx 제거
    'mimeType': 'application/vnd.google-apps.spreadsheet',  # ✅ 변환 지시
  }

  if gdrive_folder_id:
    file_metadata['parents'] = [gdrive_folder_id]

  # MIME type 설정 (csv or xlsx)
  file_ext = os.path.splitext(local_file_path)[1].lower()
  if file_ext == '.csv':
    media = MediaFileUpload(local_file_path, mimetype='text/csv')
  elif file_ext == '.xlsx':
    media = MediaFileUpload(local_file_path,
                            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
  else:
    raise ValueError("Only .csv or .xlsx files are supported.")

  file = service.files().create(
      body=file_metadata,
      media_body=media,
      fields='id'
  ).execute()

  print(
      f"✅ Google Sheets로 변환 업로드 완료: https://docs.google.com/spreadsheets/d/{file['id']}")
