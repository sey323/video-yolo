import config
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError

line_bot_api = LineBotApi(config.line_channel_access_token)
handler = WebhookHandler(config.line_channel_secret)
