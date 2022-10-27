import os

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


class GoogleDriveFacade:
    
    def __init__(self, setting_path: str='settings.yaml') -> None:
        gauth = GoogleAuth(setting_path)
        gauth.LocalWebserverAuth()

        self.drive = GoogleDrive(gauth)

    def upload(self, save_file_name: str, local_file_path: str, is_delete: bool=False):
        file = self.drive.CreateFile(
            {
                'title':save_file_name,
            }
        )
        file.SetContentFile(local_file_path)
        file.Upload()
        
        if is_delete:
            os.remove(local_file_path)
            
        image_url = f"https://drive.google.com/uc?id={str( file['id'] )}" 
        return image_url
            
        
if __name__ == "__main__":
    g = GoogleDriveFacade()
    g.upload('hello.txt')
