import os

from config import logger
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


class GoogleDriveFacade:
    def __init__(self, setting_path: str = "settings.yaml") -> None:
        gauth = GoogleAuth(setting_path)
        gauth.LocalWebserverAuth()

        self.drive = GoogleDrive(gauth)

    def create_folder(self, folder_name):
        ret = self.check_folders(folder_name)
        if ret:
            folder = ret
            logger.info(folder["title"] + " exists")
        else:
            folder = self.drive.CreateFile(
                {"title": folder_name, "mimeType": "application/vnd.google-apps.folder"}
            )
            folder.Upload()

        return folder

    def check_folders(
        self,
        folder_name,
    ):
        query = f'title = "{os.path.basename(folder_name)}"'

        list = self.drive.ListFile({"q": query}).GetList()
        if len(list) > 0:
            return list[0]
        return False

    def upload(
        self,
        save_file_name: str,
        local_file_path: str,
        save_folder_name: str = "sample",
        is_delete: bool = False,
    ):

        if save_folder_name:
            folder = self.create_folder(save_folder_name)

        file = self.drive.CreateFile(
            {"title": save_file_name, "parents": [{"id": folder["id"]}]}
        )
        file.SetContentFile(local_file_path)
        file.Upload({"convert": True})

        if is_delete:
            os.remove(local_file_path)

        drive_url = f"https://drive.google.com/uc?id={str( file['id'] )}"
        return drive_url


if __name__ == "__main__":
    g = GoogleDriveFacade()
    # g.upload('api.py', 'api.py')
