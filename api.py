from flask import Flask, request, jsonify, make_response

api = Flask(__name__)
api.config["APPLICATION_ROOT"] = "/media/v1/yt"

import src.scene_dct as scene_dct
import src.service as service
from models.YOLO_small.YOLO_small_tf import YOLO_TF as detector


# ダウンロード用API
@api.route("/download", methods=["GET"])
def get_download_youtube():
    # リクエストパラメータを取得
    params = request.args

    movie_path = params.get("movie_path")
    save_path = params.get("save_path")

    if not movie_path:
        return make_response("Please set movie path")
    if not save_path:
        save_path = "resources"

    service.download_youtube(
        movie_path, save_path=save_path,
    )

    return make_response(save_path)


# 動画分析API
@api.route("/analysis", methods=["GET"])
def get_movie_analy():
    params = request.args

    if "movie_path" in params:
        movie_path = params.get("movie_path")
    else:
        return make_response("Please set movie path")

    save_path = "test"
    if "save_path" in params:
        save_path = params.get("save_path")

    thres = 50
    if "thres" in params:
        thres = params.get("thres")

    service.cut_and_detect(
        movie_path, cut_dct, detect_ai, save_path=save_path, thres=int(thres)
    )

    return make_response(save_path)


# エラーハンドリング
@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Not found"}), 404)


if __name__ == "__main__":
    yolo = detector()
    detect_ai = yolo.detect_from_cvmat
    cut_dct = scene_dct.MAE
    api.run(host="0.0.0.0", port=3000)
