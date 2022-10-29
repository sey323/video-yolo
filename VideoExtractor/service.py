import logging
import os
from typing import Callable

import cv2
import numpy as np

from VideoExtractor.facade.google_drive_facade import GoogleDriveFacade
from VideoExtractor.facade.google_photo_facade import GooglePhotoFacade
from VideoExtractor.facade.youtube_facade import YoutubeFacade
from VideoExtractor.util import ExcelDumper

logger = logging.getLogger(__name__)
google_drive = GoogleDriveFacade()
google_photo = GooglePhotoFacade(
        credential_path = "keys/client_secrets.json",
        token_path='keys/token.pkl'
    )


def save_media(save_media_type: str, save_file_name: str, local_file_path: str, ):
    """メディアファイルを任意のストレージに保存する。

    Args:
        save_media_type (str): _description_
        save_file_name (str): _description_
        local_file_path (str): _description_

    Returns:
        _type_: _description_
    """
    if save_media_type == "local":
        return {
            "file_name": save_file_name,
            "url": local_file_path
        }
    elif save_media_type == "drive":
        url = google_drive.upload(
            save_file_name=save_file_name, 
            local_file_path=local_file_path,
            is_delete=True
        )
        return {
            "file_name": save_file_name,
            "url": url
        }
    elif save_media_type == "photo":
        response = google_photo.upload(
            save_file_name=save_file_name, 
            local_file_path=local_file_path,
            is_delete=True
        )
        return {
            "file_name": save_file_name,
            "url": response.get('productUrl')
        }
    else:
        # ファイルを削除してエラーを通知
        os.remove(local_file_path)
        return {
            "status": "error"
        }

def download_video(
    url: str,
    save_path: str,
    save_media_type: str = "local"
) -> str:
    """YoutubeのURLから動画をダウンロードし、タイトルを返す。

    Args:
        url (str): 対象のYoutubeのURL
        save_path (str): ダウンロードした画像を保存する際のパス

    Returns:
        str: urlに指定した動画のタイトル
    """
    # 保存するディレクトリが存在するか確認する．
    if not os.path.exists(os.path.join(save_path)):
        os.makedirs(os.path.join(save_path))

    video_file_name = YoutubeFacade.download_video(url, save_path)
    video_file_path = os.path.join(save_path, video_file_name)
    # 
    return save_media(
        save_media_type=save_media_type,
        save_file_name=video_file_name, 
        local_file_path=video_file_path,
    )


def download_audio(
    url: str,
    save_path: str,
    save_media_type: str = "local"
) -> str:
    """YoutubeのURLから動画を音楽に変換しダウンロードし、タイトルを返す。

    Args:
        url (str): 対象のYoutubeのURL
        save_path (str): ダウンロードした画像を保存する際のパス

    Returns:
        str: urlに指定した動画のタイトル
    """
    # 保存するディレクトリが存在するか確認する．
    if not os.path.exists(os.path.join(save_path)):
        os.makedirs(os.path.join(save_path))

    audio_file_name = YoutubeFacade.download_audio(url, save_path)
    audio_file_path = os.path.join(save_path, audio_file_name)
    # 

    return save_media(
        save_media_type=save_media_type,
        save_file_name=audio_file_name, 
        local_file_path=audio_file_path,
    )


def clip_image_from_detected(
    base_image, param_path: str, original_size_ratio: tuple = ()
) -> None:
    """画像からアノテーションされた領域のみを切り抜く

    Args:
        base_image (str): 処理をする対象の画像のパス。
        param_path (str): Yolo形式のアノテーションファイルのパス。
        original_size_ratio (tuple): (縦, 横)の順でアノテーション領域を切り抜く際のマージンサイズ。
    """
    # アノテーションファイルの読み込み
    with open(param_path, "r") as f:
        labeled_params = f.read().split("\n")[:-1]

    if labeled_params == []:  # ラベル情報が空の場合は何もしない
        return

    # 処理に利用するファイルの情報を取得
    # 2階層上のディレクトリを取得
    target_dir = os.path.dirname(os.path.dirname(param_path))
    tmp_basename = os.path.basename(param_path)
    target_basename, _ = os.path.splitext(tmp_basename)

    for index, label in enumerate(labeled_params):
        # アノテーション結果のファイルから、切り抜きに必要な情報を取得する。
        # 例: person,494,174,94,114,0.3397107720375061
        label_list = label.split(",")
        label_name = label_list[0]  # 先頭の配列はラベル名
        x, y, w, h = (
            int(float(label_list[1])),
            int(float(label_list[2])),
            int(float(label_list[3])),
            int(float(label_list[4])),
        )

        # 0.5以下のスコアの場合は保存しない
        score = float(label_list[5][0:-8])
        if score < 0.5:
            continue
        if original_size_ratio != []:
            x = int(x * original_size_ratio[1])
            y = int(y * original_size_ratio[0])
            w = int(w * original_size_ratio[1])
            h = int(h * original_size_ratio[0])
        cliped = base_image[y:h, x:w]

        # 保存用のフォルダの作成
        # target_dir/cliped/${ラベル名}のフォルダに画像を保存する
        save_dir = os.path.join(target_dir, "cliped", label_name)
        os.makedirs(save_dir, exist_ok=True)
        # 画像を保存する
        cliped_save_name = "{0}_{1}_{2}.png".format(target_basename, label_name, index)
        logger.info("save path: {}".format(os.path.join(save_dir, cliped_save_name)))
        cv2.imwrite(os.path.join(save_dir, cliped_save_name), cliped)


def cut_and_detect(
    url: str,
    cut_dct: Callable[[any, any], float],
    detect_ai: Callable[[any, str, str], None],
    save_path: str,
    threshold: float,
    label_clip: bool = True,
):
    """シーン検出と物体検出を行う

    Args:
        url (str): 対象のYoutubeのパス
        cut_dct (Callable[[any, any], float]): シーン検出に用いる関数
        detect_ai (Callable[[any, str, str], None]): シーンに適応するAIのメソッド
        save_path (str): 画像を保存するパス
        threshold (float): シーン検出に用いる閾値
        label_clip (bool): オリジナル画像からラベル画像領域を画像として保存する場合(true)
    """
    # ExcelDumperの初期化
    HTML_dumper = ExcelDumper(save_path=save_path, img_size=(640, 360))

    # パラメータの初期化
    picture_size, frame_cnt = (640, 360), 0
    frame_penult, frame_ultima = None, np.zeros((*picture_size[::-1], 3))

    try: 
        # 1秒ごとに画像を処理する．
        for frame, time in YoutubeFacade(url, save_root_path=save_path, size=None):
            if frame_penult is None:
                frame_penult = frame_ultima
            frame_ultima = cv2.resize(
                frame, picture_size, interpolation=cv2.INTER_AREA
            )  # 指定したサイズに画像を縮小

            # シーンの検出
            if cut_dct(frame_ultima, frame_penult) >= threshold:  # 閾値よりMAEが大きい場合、カットと判定
                frame_penult = frame_ultima
                formatted_time = "{:0>2}:{:0>2}".format(int(time / 60), time % 60)
                logger.info("Cut detected!: time {}".format(formatted_time))

                # AIによる処理を実施し、保存する。
                # 保存先の名前の設定
                save_param_path = os.path.join(
                    save_path, "param", "{}.txt".format(frame_cnt)
                )
                detect_ai(frame_ultima, frame_cnt, save_path)

                # ラベル付けされた領域を画像として保存する
                if label_clip:
                    original_size_ratio = tuple(
                        [x / y for (x, y) in zip(frame.shape[:2], picture_size[::-1])]
                    )
                    # 検出された領域のみ切り抜いて保存する
                    clip_image_from_detected(
                        base_image=frame,
                        param_path=save_param_path,
                        original_size_ratio=original_size_ratio,
                    )

                # シーンの情報を書き込む
                HTML_dumper.add_scene(
                    frame=frame_cnt,
                    time=formatted_time,
                    image=frame_ultima,
                    param_path=save_param_path,
                )

            frame_cnt += 1
    except Exception as e:
        print(e)

    # HTMLに保存
    HTML_dumper.save_html()
