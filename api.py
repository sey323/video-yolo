import ast
import os
from datetime import datetime as dt

from flask import Flask, jsonify, make_response, request

api = Flask(__name__)
api.config["APPLICATION_ROOT"] = "/media/v1/yt"

ANALYTICS_RESULT_PATH = os.getenv("ANALYTICS_RESULT_PATH", default="results/analytics")

AUDIO_SAVE_PATH = os.getenv("AUDIO_SAVE_PATH", default="results/audio")
VIDEO_SAVE_PATH = os.getenv("VIDEO_SAVE_PATH", default="results/video")

import VideoExtractor.service as service
from VideoExtractor.processor.object_detection import YoloV5
from VideoExtractor.processor.scene_detection import (ObjectiveSceneDetector,
                                                      SceneDetector)
from VideoExtractor.util import ImageUtil


# ダウンロード用API
@api.route("/download/video", methods=["GET"])
def get_download_video():
    # リクエストパラメータを取得
    params = request.args

    save_path = (
        os.path.join(VIDEO_SAVE_PATH, params.get("save_path"))
        if params.get("save_path")
        else VIDEO_SAVE_PATH
    )
    url = params.get("url")
    if not url:
        return make_response("Please set video path")

    response: dict = service.download_video(
        url,
        save_path=save_path,
    )

    return make_response(response)


# ダウンロード用API
@api.route("/download/audio", methods=["GET"])
def get_download_audio():
    # リクエストパラメータを取得
    params = request.args

    save_path = (
        os.path.join(AUDIO_SAVE_PATH, params.get("save_path"))
        if params.get("save_path")
        else AUDIO_SAVE_PATH
    )
    url = params.get("url")
    if not url:
        return make_response("Please set video path")

    response: dict = service.download_audio(
        url,
        save_path=save_path,
    )

    return make_response(save_path)


# 動画分析API
@api.route("/analytics", methods=["POST"])
def video_analytics():
    params = ast.literal_eval(request.data.decode("utf-8"))

    if "url" in params:
        url = params.get("url")
    else:
        return make_response("Please set video path")

    save_path_suffix = (
        params.get("save_path")
        if "save_path" in params
        else dt.now().strftime("%Y%m%d%H%M%S")
    )
    save_path = os.path.join(ANALYTICS_RESULT_PATH, save_path_suffix)
    face_threshold = int(params.get("face_threshold")) if "face_threshold" in params else 0.5
    numeric_threshold = (
        int(params.get("numeric_threshold")) if "numeric_threshold" in params else 100
    )
    scene_detector = params.get("scene_detector") if "scene_detector" in params else "numeric"

    if scene_detector == "numeric":
        # 識別方式で数字を利用する
        scene_detector = SceneDetector("MAE")
        cut_dct = scene_detector.image_distance
        threshold = numeric_threshold
    elif "target_image" in params and scene_detector == "face":
        # 識別方式が顔の時、Postに与えられた画像を保存する
        save_image_path = ImageUtil.save_image_from_base64(
            params.get("target_image"), save_path=save_path
        )
        osd = ObjectiveSceneDetector(save_image_path, numeric_threshold)
        cut_dct = osd.face_distance
        threshold = face_threshold
    else:
        return make_response("Please set target image")

    service.cut_and_detect(url, cut_dct, detect_ai, save_path=save_path, threshold=threshold)

    return make_response(save_path)


# エラーハンドリング
@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Not found"}), 404)





if __name__ == "__main__":
    detector = YoloV5()
    detect_ai = detector.predict
    cut_dct = SceneDetector.MAE
    api.run(host="0.0.0.0", port=3000)
