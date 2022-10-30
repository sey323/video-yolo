import logging

logging.basicConfig(level=logging.INFO)

import VideoExtractor.controller.SlackBot as SlackBot

if __name__ == "__main__":
    SlackBot.start()
