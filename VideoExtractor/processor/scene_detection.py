import logging

import cv2
import face_recognition
import numpy as np

logger = logging.getLogger(__name__)


class SceneDetector:
    def __init__(self, calc_method: str = "MAE"):
        self.calc_method = calc_method
        logger.info("Use method: {}".format(calc_method))

    def image_distance(self, now: np.ndarray, prev: np.ndarray) -> float:
        """入力した2枚の画像の距離を計算する。

        Args:
            now (np.ndarray): 1枚目の画像
            prev (np.ndarray): 2枚目の画像

        Returns:
            float: 計算された距離
        """
        if self.calc_method == "MAE":
            return self.MAE(now, prev)
        elif self.calc_method == "MSE":
            return self.MSE(now, prev)
        elif self.calc_method == "MAE_HSV":
            return self.MAE_HSV(now, prev)
        elif self.calc_method == "MAE_block":
            return self.MAE_block(now, prev)

    @staticmethod
    def MSE(now: np.ndarray, prev: np.ndarray) -> float:
        """Mean Square Error

        Args:
            now (np.ndarray): 現在のシーンの画像の配列
            prev (np.ndarray): 直前のシーンの配列

        Returns:
            float: 計算結果
        """
        diff = now.astype(np.int) - prev.astype(np.int)
        return np.mean(np.square(diff))

    @staticmethod
    def MAE(now: np.ndarray, prev: np.ndarray) -> float:
        """Mean Absolute Error

        Args:
            now (np.ndarray): 現在のシーンの画像の配列
            prev (np.ndarray): 直前のシーンの配列

        Returns:
            float: 計算結果
        """
        diff = now.astype(np.int) - prev.astype(np.int)
        return np.mean(np.abs(diff))

    @staticmethod
    def MAE_HSV(now: np.ndarray, prev: np.ndarray) -> float:
        """Mean Absolute Error on HSV

        Args:
            now (np.ndarray): 現在のシーンの画像の配列
            prev (np.ndarray): 直前のシーンの配列

        Returns:
            float: 計算結果
        """
        now_ = np.array(now, dtype=np.uint8)
        prev_ = np.array(prev, dtype=np.uint8)
        now_hsv = cv2.cvtColor(now_, cv2.COLOR_BGR2HSV)
        prev_hsv = cv2.cvtColor(prev_, cv2.COLOR_BGR2HSV)
        diff = now_hsv[:, :, (0, 1)].astype(np.int) - prev_hsv[:, :, (0, 1)].astype(
            np.int
        )
        return np.mean(np.abs(diff))

    @staticmethod
    def MAE_block(
        now: np.ndarray, prev: np.ndarray, picsize=(16, 9)
    ) -> float:  # mean absolute error
        now_r = cv2.resize(now, picsize, interpolation=cv2.INTER_AREA)  # 指定サイズに縮小
        prev_r = cv2.resize(prev, picsize, interpolation=cv2.INTER_AREA)
        diff = now_r.astype(np.int) - prev_r.astype(np.int)

        return np.mean(np.abs(diff))


class ObjectiveSceneDetector:
    def __init__(self, target_image_path: str, numeric_threshold: float = 60.0):
        logger.info("Load target face image: {}".format(target_image_path))
        image = face_recognition.load_image_file(target_image_path)
        loc = face_recognition.face_locations(image, model="hog")
        self.base_face_feature = face_recognition.face_encodings(image, loc)
        self.numeric_threshold = numeric_threshold

    def face_distance(self, now: np.ndarray, prev: np.ndarray) -> float:
        # 直前の画像と似ている画像であれば取得しない
        if SceneDetector.MAE(now, prev) < self.numeric_threshold:
            return 0

        loc = face_recognition.face_locations(now, model="hog")
        now_face_feature = face_recognition.face_encodings(now, loc)
        if now_face_feature == []:  # 画像に顔が写っていない場合
            return 0

        # 顔の類似度を計算
        dist = np.linalg.norm(self.base_face_feature[0] - now_face_feature[0])

        logger.info(dist)
        return dist
