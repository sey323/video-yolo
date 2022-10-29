
import os
import pickle
from pathlib import Path

import requests
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

 #各URLやスコープ 
API_SERVICE_NAME = "photoslibrary"
API_VERSION = "v1"
SCOPES = ["https://www.googleapis.com/auth/photoslibrary.appendonly"]
class GooglePhotoFacade:
    # ログインしてセッションオブジェクトを返す
    def __init__(
        self,
        credential_path: str,
        token_path: str = "",
    ):
        with build(
            API_SERVICE_NAME,
            API_VERSION,
            credentials=self._login(credential_path, token_path),
            static_discovery=False,
        ) as service:
            self.service = service
            print("Google OAuth is Complete.")

        self.credential_path = credential_path
        self.token_path = token_path
    
    def _login(self, credential_path: str, token_path: str) -> any:
        """Googleの認証を行う

        Args:
            credential_path (str): GCPから取得したclient_secret.jsonのパス
            token_path (str): Oauth2認証によって得られたトークンを保存するパス。

        Returns:
            googleapiclient.discovery.Resource: _description_
        """

        if Path(token_path).exists():
            # TOKENファイルを読み込み
            with open(token_path, "rb") as token:
                credential = pickle.load(token)
            if credential.valid:
                print("トークンが有効です.")
                return credential
            if credential and credential.expired and credential.refresh_token:
                print("トークンの期限切れのため、リフレッシュします.")
                # TOKENをリフレッシュ
                credential.refresh(Request())
        else:
            print("トークンが存在しないため、作成します.")
            # TOKENファイルがない場合は認証フローを起動する(Default: host=localhost, port=8080)
            credential = InstalledAppFlow.from_client_secrets_file(
                credential_path, SCOPES
            ).run_local_server()

        # CredentialをTOKENファイルとして保存
        with open(token_path, "wb") as token:
            pickle.dump(credential, token)

        return credential

    def upload(self, save_file_name: str, local_file_path: str, is_delete: bool=False):
        
        self._login(self.credential_path, self.token_path) # トークンの期限を確認
        
        with open(str(local_file_path), 'rb') as image_data:
            url = 'https://photoslibrary.googleapis.com/v1/uploads'
            headers = {
                'Authorization': "Bearer " + self.service._http.credentials.token,
                'Content-Type': 'application/octet-stream',
                'X-Goog-Upload-File-Name': save_file_name.encode(),
                'X-Goog-Upload-Protocol': "raw",
            }
            response = requests.post(url, data=image_data.raw, headers=headers)

        upload_token = response.content.decode('utf-8')
        print("Google Photoへのアップロードが完了しました。")
        body = {
            'newMediaItems': [{"simpleMediaItem": {'uploadToken': upload_token}}]
        }
        
        upload_response = self.service.mediaItems().batchCreate(body=body).execute()
        print("Google Photoへのアップロードした動画の登録に成功しました。")
        
        if is_delete:
            os.remove(local_file_path)
        
        # uploadしたURLを返す
        return upload_response['newMediaItemResults'][0]['mediaItem']

if __name__ == "__main__":
    g = GooglePhotoFacade(
        credential_path = "keys/client_secrets.json",
        token_path='keys/token.pkl'
    )
    g.upload(
        save_file_name = "一度見たら忘れられない渋谷の美しい夜景 - 4K UHD.mp4",
        local_file_path = "results/analytics/test/一度見たら忘れられない渋谷の美しい夜景 - 4K UHD.mp4",
        is_delete=True
    )
