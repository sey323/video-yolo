import logging
import os

import cv2
import yt_dlp
from VideoExtractor.util import FileUtil

logger = logging.getLogger(__name__)


class YoutubeFacade(object):
    """
    Youtubeから動画をダウンロードし、フレームごとの画像を返す。
    """

    def __init__(
        self,
        video_file,
        size=None,
        inter_method=cv2.INTER_AREA,
        save_root_path="resources",
    ):
        logger.info(f"video file is {video_file}")
        if not os.path.exists(save_root_path):
            os.makedirs(save_root_path)

        if os.path.isfile(video_file):  # mp4ファイルが存在するとき
            logger.info("Loading video file from local.")
            self.org = cv2.VideoCapture(video_file)
        else:  # MP4がないときはYoutubeからダウンロード
            logger.info("Download video from Youtube.")
            self.download_video(video_file, save_root_path)
            download_url = FileUtil.get_latest_modified_file_path(os.path.join(save_root_path))
            self.org = cv2.VideoCapture(download_url)

        self.frame_count = 0
        self.size = size  # frame size
        self.inter_method = inter_method

    def __iter__(self):
        return self

    def __next__(self):
        self.end_flg, self.frame = self.org.read()
        if not self.end_flg:  # end of the video
            raise StopIteration()
        self.frame_count += 1
        if self.size:  # resize when size is specified
            self.frame = cv2.resize(
                self.frame, self.size, interpolation=self.inter_method
            )
        return self.frame, self.get_time()

    def __del__(self):  # anyway it works without destructor
        self.org.release()

    def get_time(self) -> int:
        """fpsから計算し、現在の動画の秒数を計算する．

        Returns:
            int: 動画の現在の秒数
        """

        fps = self.org.get(cv2.CAP_PROP_FPS)
        return int(self.frame_count / fps)

    def get_size(self):
        """動画の解像度を返す

        Returns:
            (int, int):　(w, h)
        """
        return (
            int(self.org.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self.org.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )

    def get_fps(self) -> float:
        """動画のFpsを返す

        Returns:
            float: fps
        """
        return self.org.get(cv2.CAP_PROP_FPS)

    @staticmethod
    def download_video(url: str, save_path: str):
        """YouTubeからダウンロードする、動画

        Args:
            url (str): 読み込む動画のURL
            save_path (str): ダウンロードした動画を保存するパス
        """
        ydl_opts = {
            'format': 'best',
            "outtmpl": f"{save_path}/%(title)s.%(ext)s",
            # "cookies-from-browser": "Vivaldi",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.download(
                url, 
            )
            save_full_path = FileUtil.get_latest_modified_file_path(save_path)

        return os.path.basename(save_full_path)

    @staticmethod
    def download_audio(url: str, save_path: str):
        """YouTubeからダウンロードする、音声ファイル

        Args:
            url (str): 読み込む動画のURL
            save_path (str): ダウンロードした動画を保存するパス
        """
        ydl_opts = {
            "outtmpl": f"{save_path}/%(title)s.%(ext)s",
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.download(
                url, 
            )
            save_full_path = FileUtil.get_latest_modified_file_path(save_path)

        return os.path.basename(save_full_path)


