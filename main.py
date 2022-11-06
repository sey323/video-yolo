import argparse
import os

import config
import VideoExtractor.service as service
from config import logger
from VideoExtractor.processor import yolo_v5_ai
from VideoExtractor.processor.scene_detection import (
    ObjectiveSceneDetector,
    SceneDetector,
)


def main(args):
    # YOLO検出検出器
    save_path = os.path.join(config.analytics_result_base_path, args.save_path)

    # 検出関数の定義
    if args.scene_detector == "face":
        logger.info("Use face recognize.")
        face_detector = ObjectiveSceneDetector(
            args.target_image_path, numeric_threshold=args.numeric_threshold
        )
        scene_cut_process = face_detector.face_distance
        cut_threshold = args.face_threshold
    elif args.scene_detector == "numeric":
        logger.info("Use scene detect. use method: {}".format(args.cut_method))
        scene_detector = SceneDetector(args.cut_method)
        scene_cut_process = scene_detector.image_distance
        cut_threshold = args.numeric_threshold
    # 処理の実行
    service.cut_and_detect(
        args.url, scene_cut_process, yolo_v5_ai.predict, save_path, cut_threshold
    )


if __name__ == "__main__":
    # 引数の設定
    parser = argparse.ArgumentParser()

    parser.add_argument("url", type=str, help="処理を行う動画のURL。ローカルその動画へのパスを指定する。")
    parser.add_argument(
        "--save_path", type=str, default="test", help="ダウンロードした動画や検出結果を保存するディレクトリへのパス"
    )
    parser.add_argument(
        "--scene_detector",
        default="numeric",
        type=str,
        help="シーンをカットする方法(face: --target_image_pathで指定した顔画像が出現した場合。, numeric: 直前のフレームとの差分)",
    )
    parser.add_argument(
        "--target_image_path",
        default="",
        type=str,
        help="scene_detector=faceの時、検出対象の顔画像のパス",
    )
    parser.add_argument(
        "--face_threshold",
        default=0.4,
        type=float,
        help="scene_detector=faceの時、シーンをカットする変数の閾値",
    )
    parser.add_argument(
        "--cut_method",
        default="MAE",
        type=str,
        help="scene_detector=numericの時、シーンをカットするメソッド(MAE, MSE, MAE_HSV, MAE_block)",
    )
    parser.add_argument(
        "--numeric_threshold",
        default=50.55679398148148,
        type=float,
        help="scene_detector=numericの時、シーンをカットする変数の閾値",
    )

    args = parser.parse_args()
    main(args)
