from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


class GoogleDriveFacade:
    
    def __init__(self, setting_path: str='settings.yaml') -> None:
        gauth = GoogleAuth(setting_path)
        gauth.LocalWebserverAuth()

        self.drive = GoogleDrive(gauth)

    def upload(self, save_file_name: str, local_file_path: str):
        file = self.drive.CreateFile(
            {
                'title':save_file_name,
                # 'mimeType': 'image/jpeg',
            }
        )
        file.SetContentFile(local_file_path)
        file.Upload()
        
if __name__ == "__main__":
    g = GoogleDriveFacade()
    g.upload('hello.txt')
