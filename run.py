import logging
import os

logging.basicConfig(level=logging.INFO)

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient

import config
from VideoExtractor import service

app = App(token=config.slack_bot_token)
VIDEO_SAVE_PATH = os.getenv("VIDEO_SAVE_PATH", default="results/video")

# イベント API
@app.message(r'(https?|ftp)(:\/\/[\w\/:%#\$&\?\(\)~\.=\+\-]+)')
def download_from_youtube(message, say):
    say(f"動画のダウンロードを開始します。")
    response: dict = service.download_video(
        message['text'][1:-1],
        save_path=VIDEO_SAVE_PATH,
    )
    say(f"""ダウンロードが完了しました。
        ファイル名: {response.get('file_name')}
        URL: {response.get('url')}
        """)

@app.event("message")
@app.event("app_mention")
def handle_app_mention_events(body, logger):
    logger.info(body)

if __name__ == "__main__":
    handler = SocketModeHandler(app, config.slack_api_token)
    handler.start()
