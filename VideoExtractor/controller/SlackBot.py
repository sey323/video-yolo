import json
import os
from datetime import datetime as dt

import config
from config import logger
from cv2 import threshold
from slack_bolt import Ack, App, BoltContext, Say
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from VideoExtractor import service
from VideoExtractor.processor import yolo_v5_ai
from VideoExtractor.processor.scene_detection import (ObjectiveSceneDetector,
                                                      SceneDetector)

app = App(token=config.slack_bot_token)

# イベント API
@app.message(r'(https)(:\/\/[\w\/:%#\$&\?\(\)~\.=\+\-]+)')
def download_from_youtube(message, say):
    say(f"動画のダウンロードを開始します。デフォルトのGoogleDriveに保存します。")
    response: dict = service.download_video(
        message['text'][1:-1],
        save_path=config.video_save_path,
        save_media_type="drive"
    )
    say(f"""ダウンロードが完了しました。
        ファイル名: {response.get('file_name')}
        URL: {response.get('url')}
        """)

# ショートカットとモーダル
@app.shortcut("download_from_youtube")
def download_from_youtube_shortcut(
    ack: Ack, 
    body: dict,
    context: BoltContext, 
    client: WebClient
):
    ack()
    
    modal_view = _load_view("VideoExtractor/controller/view/download_modal.json")
    if context.channel_id is None:
        modal_view["blocks"].append(
            _load_view("VideoExtractor/controller/view/channel_block.json")
        )
    else:
        state = {"channel_id": context.channel_id}
        modal_view["private_metadata"] = json.dumps(state)
    client.views_open(
        trigger_id=body["trigger_id"],
        view=modal_view
    )


# ショートカットとモーダル
@app.shortcut("analytics_video")
def analytics_video_shortcut(
    ack: Ack, 
    body: dict,
    context: BoltContext, 
    client: WebClient
):
    ack()
    
    modal_view = _load_view("VideoExtractor/controller/view/analytics_modal.json")
    if context.channel_id is None:
        modal_view["blocks"].append(
            _load_view("VideoExtractor/controller/view/channel_block.json")
        )
    else:
        state = {"channel_id": context.channel_id}
        modal_view["private_metadata"] = json.dumps(state)
    client.views_open(
        trigger_id=body["trigger_id"],
        view=modal_view
    )


@app.view("download_from_youtube")
def download_process_start(ack: Ack, view: dict, say: Say):
    ack()
    
    # 通知するチャンネルの取得
    private_metadata: dict = json.loads(view.get("private_metadata"))
    if "channel_id" in private_metadata.keys():
        channel_to_notify = private_metadata.get('channel_id')
    else:
        channel_to_notify = (
            view["state"]["values"]
            .get("channel_to_notify")
            .get("_")
            .get("selected_conversation")
        )
    say(channel=channel_to_notify,
        text=f"ダウンロードを開始します。")

    url: str = view['state']['values']['url']['input']['value']
    fmt: str = view['state']['values']['fmt']['selected_fmt']['selected_option']['value']
    save_media_type: str = view['state']['values']['media_type']['selected_media_type']['selected_option']['value']

    try:
        # ダウンロード処理    
        if fmt == "mp4":
            # say(f"動画のダウンロードを開始します。")
            response: dict = service.download_video(
                url,
                save_path=config.video_save_path,
                save_media_type=save_media_type
            )
        elif fmt == "mp3":
            response: dict = service.download_audio(
                url,
                save_path=config.audio_save_path,
                save_media_type=save_media_type
            )
        else:
            response = None
    except Exception as e:
        say(
            channel=channel_to_notify,
            text=f"""ダウンロード処理に失敗しました。以下エラー内容。
```{e}```"""
        )
    # そのチャンネルに対して chat.postMessage でメッセージを送信します
    say(
        channel=channel_to_notify,
        text=f"""ダウンロードが完了しました。
        ファイル名: {response.get('file_name')}
        URL: {response.get('url')}"""
        )


@app.view("analytics_video")
def analytics_video_start(ack: Ack, view: dict, say: Say):
    ack()
    
    # 通知するチャンネルの取得
    private_metadata: dict = json.loads(view.get("private_metadata"))
    if "channel_id" in private_metadata.keys():
        channel_to_notify = private_metadata.get('channel_id')
    else:
        channel_to_notify = (
            view["state"]["values"]
            .get("channel_to_notify")
            .get("_")
            .get("selected_conversation")
        )
    url: str = view['state']['values']['url']['input']['value']
    scene_detector: str = view['state']['values']['scene_detector']['selected_scene_detector']['selected_option']['value']
    numeric_threshold: str = view['state']['values']['numeric_threshold']['input_numeric_threshold']['value']

    say(channel=channel_to_notify,
        text=f"""動画の解析を開始します。
        URL :{url}
        解析タイプ: {'顔画像の類似度' if scene_detector == "face" else '直前のフレームとの差分'}
        閾値: {numeric_threshold}
        """)
    
    timestamp_str = dt.now().strftime('%Y%m%d_%H%M%S')
    try: 
        if scene_detector == "numeric":
            response = service.cut_and_detect(
                url,
                SceneDetector("MAE").image_distance,
                yolo_v5_ai.predict,
                save_path= os.path.join(config.analytics_result_base_path,timestamp_str),
                threshold=float(numeric_threshold) * 100 # MAEは0-100の範囲で出力されるため、顔認識の場合と合わせるために100倍する
            )
        elif scene_detector == "face":
            face_image_url: str = view['state']['values']['face_image_url']['face_image_url_text_input']['value']
            
            response = service.cut_and_detect(
                url,
                ObjectiveSceneDetector(
                    face_image_url, numeric_threshold=float(numeric_threshold)
                ).face_distance,
                yolo_v5_ai.predict,
                save_path= os.path.join(config.analytics_result_base_path,timestamp_str),
                threshold=float(numeric_threshold) 
            )
    except Exception as e:
        say(
            channel=channel_to_notify,
            text=f"""解析処理に失敗しました。以下エラー内容。
```{e}```"""
        )
        
    # そのチャンネルに対して chat.postMessage でメッセージを送信します
    say(
        channel=channel_to_notify,
        text=f"""解析処理が完了しました。
        ファイル名: {response.get('title')}
        URL: {response.get('url')}"""
        )


@app.event("message")
@app.event("app_mention")
def handle_app_mention_events(body, logger):
    logger.info(body)

def start():
    handler = SocketModeHandler(app, config.slack_api_token)
    handler.start()

def _load_view(file_path: str) -> dict:
    with open(file_path) as f:
        return json.load(f)
