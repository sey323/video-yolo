from os import environ

from dotenv import load_dotenv

load_dotenv()

slack_api_token = environ.get("SLACK_APP_TOKEN", '')
slack_bot_token = environ.get("SLACK_BOT_TOKEN", '')
