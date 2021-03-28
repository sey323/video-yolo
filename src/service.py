import os
import cv2
import numpy as np
from src.movie import MovieIter
from src.dump import Dumper


def download_youtube(
    movie_path, save_path,
):
    """
    Youtubeから動画をダウンロードする
    """
    # 保存するディレクトリが存在するか確認する．
    save_folders = "results/" + save_path
    if not os.path.exists(os.path.join(save_folders)):
        os.makedirs(os.path.join(save_folders))

    yt_title = MovieIter.youtube_downloader(movie_path, save_path)


def cut_and_detect(
    movie_path, cut_dct, detect_ai, save_path, thres, img_size=[240, 135]
):
    """
    シーン検出と物体検出を行う．
    Parameters
    ----------
    cut_dct : function(now , before)
        現在のフレームと1つ前のフレームを見てカット位置か確認する．
    """
    picsize = (640, 360)

    frame_cnt = 0
    frame_ultima = np.zeros((*picsize[::-1], 3))  # create empty image

    HTML_dumper = Dumper(save_path="results/{}/".format(save_path), img_size=img_size)

    # 保存するディレクトリが存在するか確認する．
    save_folders = "results/" + save_path
    if save_folders and not os.path.exists(os.path.join(save_folders, "img")):
        os.makedirs(os.path.join(save_folders, "img"))
        os.makedirs(os.path.join(save_folders, "exel"))
        os.makedirs(os.path.join(save_folders, "param"))

    # 1秒ごとに画像を処理する．
    frame_penult = None
    for frame, time in MovieIter(movie_path, None):
        if frame_penult is None:
            frame_penult = frame_ultima
        frame_ultima = cv2.resize(
            frame, picsize, interpolation=cv2.INTER_AREA
        )  # 指定サイズに縮小

        # シーンの検出
        if cut_dct(frame_ultima, frame_penult) >= thres:  # 閾値よりMAEが大きい場合、カットと判定
            frame_penult = frame_ultima

            formatted_time = "{:0>2}:{:0>2}".format(int(time / 60), time % 60)
            print("Cut detected!: time {}".format(formatted_time))
            # 保存先の名前の設定
            save_img_path = "results/{}/img/{}.jpg".format(save_path, frame_cnt)
            save_half_img_path = "results/{}/exel/{}.jpg".format(save_path, frame_cnt)
            save_param_path = "results/{}/param/{}.txt".format(save_path, frame_cnt)
            detect_ai(
                frame_ultima, tofile_img=save_img_path, tofile_txt=save_param_path
            )

            # 画像のリサイズ処理
            img = cv2.imread(save_img_path, cv2.IMREAD_COLOR)
            resize = (img_size[0], img_size[1])
            half_img = cv2.resize(frame_ultima, resize, interpolation=cv2.INTER_AREA)
            cv2.imwrite(save_half_img_path, half_img)

            HTML_dumper.add_scene(frame_cnt, formatted_time, save_param_path)

        frame_cnt += 1

    # HTMLに保存
    HTML_dumper.save_html()
