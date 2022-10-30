import logging
from os import environ

from dotenv import load_dotenv

load_dotenv()

slack_api_token = environ.get("SLACK_APP_TOKEN", '')
slack_bot_token = environ.get("SLACK_BOT_TOKEN", '')

video_save_path = environ.get("VIDEO_SAVE_PATH", "results/video")
audio_save_path = environ.get("AUDIO_SAVE_PATH", "results/audio")
analytics_result_base_path = environ.get("ANALYTICS_RESULT_BASE_PATH", "results/analytics")


logging.basicConfig(format="[%(levelname)s] %(asctime)s %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
