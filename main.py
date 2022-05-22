import argparse
import logging
import os

import src.scenedct as scenedct
import src.service as service
from src.models import Yolov5Torch

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def main(args):
    # YOLO検出検出器
    ANALYSIS_RESULT_PATH = os.getenv("ANALYSIS_RESULT_PATH", default="results/analysis")
    save_path = os.path.join(ANALYSIS_RESULT_PATH, args.save_path)
    detector = Yolov5Torch()
    detect_ai = detector.predict

    # 検出関数の定義
    if args.scenedct == "face":
        logger.info("Use face recognize.")
        frdetector = scenedct.ObjectiveSceneDetector(
            args.target_image_path, numeric_thres=args.numeric_thres
        )
        cut_dct = frdetector.face_distance
        cut_thres = args.face_thres
    elif args.scenedct == "numeric":
        logger.info("Use scene detect. use method: {}".format(args.calc_method))
        sdetector = scenedct.SceneDetector(args.calc_method)
        cut_dct = sdetector.image_distance
        cut_thres = args.numeric_thres
    # 処理の実行
    service.cut_and_detect(args.url, cut_dct, detect_ai, save_path, cut_thres)


if __name__ == "__main__":
    # 引数の設定
    parser = argparse.ArgumentParser()

    parser.add_argument("url", type=str, help="処理を行う動画のURL。ローカルその動画へのパスを指定する。")
    parser.add_argument(
        "--save_path", type=str, default="test", help="ダウンロードした動画や検出結果を保存するディレクトリへのパス"
    )
    parser.add_argument(
        "--scenedct",
        default="face",
        type=str,
        help="シーンをカットする方法(face: --target_image_pathで指定した顔画像が出現した場合。, numeric: 直前のフレームとの差分)",
    )
    parser.add_argument(
        "--target_image_path", default="", type=str, help="scenedct=faceの時、検出対象の顔画像のパス"
    )
    parser.add_argument(
        "--face_thres", default=0.4, type=float, help="scenedct=faceの時、シーンをカットする変数の閾値"
    )
    parser.add_argument(
        "--calc_method",
        default="MAE",
        type=str,
        help="scenedct=numericの時、シーンをカットするメソッド(MAE, MSE, MAE_HSV, MAE_block)",
    )
    parser.add_argument(
        "--numeric_thres",
        default=50.55679398148148,
        type=float,
        help="scenedct=numericの時、シーンをカットする変数の閾値",
    )

    args = parser.parse_args()
    main(args)
