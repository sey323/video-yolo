import io
import os
import re
from datetime import datetime

import requests
import torch
from config import logger
from PIL import Image
from RealESRGAN import RealESRGAN


class RealEsrgan:
    def __init__(self, scale=4) -> None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = RealESRGAN(device, scale=scale)
        self.model.load_weights('weights/RealESRGAN_x4.pth', download=True)
        self.output_folder = "results/sr"
        
    def _download_url(self, download_url: str, auth: str =""):
        content = requests.get(
            download_url,
            allow_redirects=True,
            headers={'Authorization': f'Bearer {auth}'},
            stream=True
        ).content
        
        return io.BytesIO(content)
        
    
    def predict(self, image_path: str, download_auth: str=""):        
        if re.match("https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", image_path): # urlの時
            logger.info(f"URLからダウンロードします. {image_path}")
            image_path = self._download_url(image_path, download_auth)
            save_file_name = f"sv_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        else:
            save_file_name = f"sv_{os.path.basename(image_path)}"
        image = Image.open(image_path).convert('RGB')

        logger.info("高解像度化処理を開始します。")
        sr_image = self.model.predict(image)
        
        save_path = os.path.join(self.output_folder, save_file_name)
        sr_image.save(save_path)
        
        return {
            "file_name": save_path
        }
        
        
        

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path", type=str, help="処理を行う画像のパス")
    args = parser.parse_args()
    
    er = RealEsrgan()
    
    er.predict(args.image_path)
