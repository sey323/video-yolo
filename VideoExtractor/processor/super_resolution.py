import numpy as np
import torch
from config import logger
from PIL import Image
from RealESRGAN import RealESRGAN


class RealEsrgan:
    def __init__(self, scale=4) -> None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = RealESRGAN(device, scale=scale)
        self.model.load_weights('weights/RealESRGAN_x4.pth', download=True)

    def predict(self, image_path: str):
        logger.info("高解像度化処理を開始します。")

        image = Image.open(image_path).convert('RGB')
        sr_image = self.model.predict(image)
        sr_image.save('results/sr_image.png')


if __name__ == "__main__":
    er = RealEsrgan()
    
    er.predict('results/moments_273839186140641.jpg')
