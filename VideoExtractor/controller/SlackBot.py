import json

import config
from config import logger
from slack_bolt import Ack, App, BoltContext, Say
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from VideoExtractor import service

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
    
    modal_view = {
            "type": "modal",
            "callback_id": "download_from_youtube",
            "title": {"type": "plain_text", "text": "Youtubeからダウンロード"},
            "submit": {"type": "plain_text", "text": "送信"},
            "close": {"type": "plain_text", "text": "キャンセル"},
            "private_metadata": "{}",
            "blocks": [
                {
                    "type": "input",
                    "block_id": "url",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "input",
                        # "multiline": True,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "YoutubeのURLを入力してください。",
                        },
                        "focus_on_load": True,
                    },
                    "label": {"type": "plain_text", "text": "url"},
                },
                {
                    "type": "input",
                    "block_id": "fmt",
                    "element": {
                        "type": "static_select",
                        "action_id": "selected_fmt",
                        "placeholder": {"type": "plain_text", "text": "ダウンロードするフォーマットを選択してください。"},
                        "initial_option": {"text": {"type": "plain_text", "text": "動画"}, "value": "mp4"},
                        "options": [
                            {"text": {"type": "plain_text", "text": "動画"}, "value": "mp4"},
                            {"text": {"type": "plain_text", "text": "音楽"}, "value": "mp3"}
                        ],
                    },
                    "label": {"type": "plain_text", "text": "保存形式"},
                },
                {
                    "type": "input",
                    "block_id": "media_type",
                    "element": {
                        "type": "static_select",
                        "action_id": "selected_media_type",
                        "placeholder": {"type": "plain_text", "text": "アップロードするメディアのタイプを選択してください。"},
                        "initial_option": {"text": {"type": "plain_text", "text": "Google Photo"}, "value": "photo"},
                        "options": [
                            {"text": {"type": "plain_text", "text": "Google Photo"}, "value": "photo"},
                            {"text": {"type": "plain_text", "text": "Google Drive"}, "value": "drive"},
                            {"text": {"type": "plain_text", "text": "ローカル"}, "value": "local"},
                        ],
                    },
                    "label": {"type": "plain_text", "text": "保存するメディア"},
                },
            ],
        }
    # conversations_select のブロックを置いてそこでチャンネルを指定してもらいます
    if context.channel_id is None:
        modal_view["blocks"].append(
            {
                "type": "input",
                "block_id": "channel_to_notify",
                "element": {
                    "type": "conversations_select",
                    "action_id": "_",
                    # response_urls を発行するためには
                    # このオプションを設定しておく必要があります
                    "response_url_enabled": True,
                    # 現在のチャンネルを初期値に設定するためのオプション
                    "default_to_current_conversation": True,
                },
                "label": {
                    "type": "plain_text",
                    "text": "起動したチャンネル",
                },
            }
        )
    else:
        # private_metadata に文字列として JSON を渡します
        # スラッシュコマンドやメッセージショートカットは必ずチャンネルがあるのでこれだけで OK
        import json
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
        text=f"動画のダウンロードを開始します。")

    url: str = view['state']['values']['url']['input']['value']
    fmt: str = view['state']['values']['fmt']['selected_fmt']['selected_option']['value']
    save_media_type: str = view['state']['values']['media_type']['selected_media_type']['selected_option']['value']

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
    # そのチャンネルに対して chat.postMessage でメッセージを送信します
    say(
        channel=channel_to_notify,
        text=f"""ダウンロードが完了しました。
        ファイル名: {response.get('file_name')}
        URL: {response.get('url')}"""
        )


@app.event("message")
@app.event("app_mention")
def handle_app_mention_events(body, logger):
    logger.info(body)


def start():
    handler = SocketModeHandler(app, config.slack_api_token)
    handler.start()
