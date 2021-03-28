from absl import app
from absl import flags

import src.scene_dct as scene_dct
import src.service as service

from models.YOLO_small.YOLO_small_tf import YOLO_TF as detector


def main(argv):
    # YOLO検出検出器
    yolo = detector()
    detect_ai = yolo.detect_from_cvmat

    # 検出関数の定義
    cut_dct = scene_dct.MAE_block

    # 処理の実行
    service.cut_and_detect(
        FLAGS.movie_path, cut_dct, detect_ai, FLAGS.save_path, FLAGS.thres
    )


if __name__ == "__main__":
    FLAGS = flags.FLAGS

    flags.DEFINE_string("movie_path", "", "処理を行う動画のURL")
    flags.DEFINE_string("save_path", "test", "生成した画像を保存するディレクトリのパス")
    flags.DEFINE_float("thres", 55.55679398148148, "シーンをカットする変数の閾値")

    app.run(main)
