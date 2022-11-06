import logging
import os

from dotenv import load_dotenv

load_dotenv()

slack_api_token = os.environ.get("SLACK_APP_TOKEN", "")
slack_bot_token = os.environ.get("SLACK_BOT_TOKEN", "")

video_save_path = os.environ.get("VIDEO_SAVE_PATH", "results/video")
audio_save_path = os.environ.get("AUDIO_SAVE_PATH", "results/audio")
analytics_result_base_path = os.environ.get(
    "ANALYTICS_RESULT_BASE_PATH", "results/analytics"
)
super_resolution_result_base_path = os.environ.get(
    "SUPER_RESOLUTION_RESULT_BASE_PATH", "results/super_resolution"
)

# 保存するフォルダを作成
os.makedirs(video_save_path, exist_ok=True)
os.makedirs(audio_save_path, exist_ok=True)
os.makedirs(analytics_result_base_path, exist_ok=True)
os.makedirs(super_resolution_result_base_path, exist_ok=True)

logging.basicConfig(
    format="[%(levelname)s] %(asctime)s %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
