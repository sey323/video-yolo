import ast
import os
from datetime import datetime as dt

import config
from flask import Flask, jsonify, make_response, request

api = Flask(__name__)
api.config["APPLICATION_ROOT"] = "/media/v1/yt"

import VideoExtractor.service as service
from VideoExtractor.controller import yolo_v5_ai
from VideoExtractor.processor.scene_detection import (ObjectiveSceneDetector,
                                                      SceneDetector)
from VideoExtractor.util import ImageUtil


# ダウンロード用API
@api.route("/download/video", methods=["GET"])
def get_download_video():
    # リクエストパラメータを取得
    params = request.args
    
    save_media_type = (
        params.get("save_media_type")
        if params.get("save_path")
        else "photo"
    )
    
    # 「save_media_type=local」の場合、ローカルに保存するパスを指定
    save_path = (
        os.path.join(config.video_save_path, params.get("save_path"))
        if params.get("save_path")
        else config.video_save_path
    )
    
    url = params.get("url")
    if not url:
        return make_response("Please set video path")

    response: dict = service.download_video(
        url,
        save_path=save_path,
        save_media_type=save_media_type
    )

    return make_response(response)


# ダウンロード用API
@api.route("/download/audio", methods=["GET"])
def get_download_audio():
    # リクエストパラメータを取得
    params = request.args

    save_media_type = (
        params.get("save_media_type")
        if params.get("save_path")
        else "local"
    )
    
    # 「save_media_type=local」の場合、ローカルに保存するパスを指定
    save_path = (
        os.path.join(config.audio_save_path, params.get("save_path"))
        if params.get("save_path")
        else config.audio_save_path
    )
    url = params.get("url")
    if not url:
        return make_response("Please set video path")

    response: dict = service.download_audio(
        url,
        save_path=save_path,
        save_media_type=save_media_type
    )

    return make_response(response)


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
    save_path = os.path.join(config.analytics_result_path, save_path_suffix)
    face_threshold = int(params.get("face_threshold")) if "face_threshold" in params else 0.5
    numeric_threshold = (
        int(params.get("numeric_threshold")) if "numeric_threshold" in params else 100
    )
    scene_detector = params.get("scene_detector") if "scene_detector" in params else "numeric"

    if scene_detector == "numeric":
        # 識別方式で数字を利用する
        scene_detector = SceneDetector("MAE")
        scene_cut_process = scene_detector.image_distance
        threshold = numeric_threshold
    elif "target_image" in params and scene_detector == "face":
        # 識別方式が顔の時、Postに与えられた画像を保存する
        save_image_path = ImageUtil.save_image_from_base64(
            params.get("target_image"), save_path=save_path
        )
        osd = ObjectiveSceneDetector(save_image_path, numeric_threshold)
        scene_cut_process = osd.face_distance
        threshold = face_threshold
    else:
        return make_response("Please set target image")

    service.cut_and_detect(url, scene_cut_process, yolo_v5_ai.predict, save_path=save_path, threshold=threshold)

    return make_response(save_path)


# エラーハンドリング
@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Not found"}), 404)

