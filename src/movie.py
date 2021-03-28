import os
import cv2
from glob import glob
from pytube import YouTube


class MovieIter(object):
    """
    Youtubeから動画をダウンロードし、フレームごとの画像を返す。
    """

    def __init__(self, moviefile, size=None, inter_method=cv2.INTER_AREA):
        save_root_path = "./resources"
        if not os.path.exists(save_root_path):
            os.makedirs(save_root_path)
        if os.path.isfile(moviefile):  # mp4ファイルが存在するとき
            print("[Loading]\tLoading Movie")
            self.org = cv2.VideoCapture(moviefile)
        else:  # MP4がないときはYoutubeからダウンロード
            print("[Download]\tDownloadMovie")
            self.youtube_downloader(moviefile, save_root_path)
            dnld_movie_path = self.get_latest_modified_file_path(save_root_path)
            self.org = cv2.VideoCapture(dnld_movie_path)

        self.framecnt = 0
        self.size = size  # frame size
        self.inter_method = inter_method

    def __iter__(self):
        return self

    def __next__(self):
        self.end_flg, self.frame = self.org.read()
        if not self.end_flg:  # end of the movie
            raise StopIteration()
        self.framecnt += 1
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
        return int(self.framecnt / fps)

    def get_size(self) -> (int, int):
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
    def youtube_downloader(url: str, save_path: str):
        """YouTubeからダウンロードする

        Args:
            url (str): 読み込む動画のURL
            save_path (str): ダウンロードした動画を保存するパス
        """
        yt = YouTube(url)
        try:
            yt.streams.get_by_itag(137).download(save_path)
        except AttributeError:
            yt.streams.get_highest_resolution().download(save_path)
        return yt.title

    def get_latest_modified_file_path(self, dirname: str) -> str:
        """ディレクトリ内で最新に更新されたファイルを得る．

        Args:
            dirname (str): 検索対象のディレクトリ

        Returns:
            str: 検索結果のファイルのフルパス
        """
        target = os.path.join(dirname, "*")
        files = [(f, os.path.getmtime(f)) for f in glob(target)]
        latest_modified_file_path = sorted(files, key=lambda files: files[1])[-1]
        return latest_modified_file_path[0]
