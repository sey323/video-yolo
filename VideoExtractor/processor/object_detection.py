import logging
import os

import cv2
import numpy as np
import torch

logger = logging.getLogger(__name__)


class YoloV5(object):
    def __init__(self):
        # Model
        self.model = torch.hub.load("ultralytics/yolov5", "yolov5s", pretrained=True)
        self.out_columns = ["name", "xmin", "ymin", "xmax", "ymax", "confidence"]
        self.save_path = ""

    def predict(
        self, image: np.ndarray, file_name_prefix: str = "tmp", save_path: str = ""
    ):
        """画像に対してYOLOによる検出を行い、保存する。

        Args:
            image (np.ndarray): [description]
            file_name_prefix (str, optional): 保存するファイルの拡張子抜きのファイル名. Defaults to "tmp".
        """
        self.save_path = save_path
        os.makedirs(os.path.join(save_path, "param"), exist_ok=True)
        os.makedirs(os.path.join(save_path, "img"), exist_ok=True)
        # Inference
        results = self.model([image])
        logger.debug(results.pandas().xyxy[0])
        self._save_results(results, file_name_prefix)

    def _save_results(self, results, file_name_prefix: str):
        """実験結果を保存する

        Args:
            results ([type]): modelの出力
            file_name_prefix (str): 保存するファイルの拡張子抜きのファイル名
        """
        # 実験結果を出力
        results.pandas().xyxy[0].to_csv(
            os.path.join(self.save_path, "param", "{}.txt".format(file_name_prefix)),
            columns=self.out_columns,
            header=False,
            index=False,
        )
        results.render()
        # 画像に保存
        cv2.imwrite(
            os.path.join(self.save_path, "img", "{}.jpg".format(file_name_prefix)),
            results.ims[0],
        )
