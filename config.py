from os import environ

from dotenv import load_dotenv

load_dotenv()

line_channel_access_token = environ.get("LINE_CHANNEL_ACCESS_TOKEN", '')
line_channel_secret = environ.get("LINE_CHANNEL_SECRET", '')
