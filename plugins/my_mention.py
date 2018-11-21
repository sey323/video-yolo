
# coding: utf-8
import sys ,os
sys.path.append( os.pardir )

from datetime import datetime, timedelta, date

from slackbot.bot import respond_to     # @botname: で反応するデコーダ
from slackbot.bot import listen_to     # @botname: で反応するデコーダ
from slackbot.bot import default_reply

import requests
import re


# @respond_to('string')     bot宛のメッセージ
#                           stringは正規表現が可能 「r'string'」
# @listen_to('string')      チャンネル内のbot宛以外の投稿
#                           @botname: では反応しないことに注意
#                           他の人へのメンションでは反応する
#                           正規表現可能
# @default_reply()          DEFAULT_REPLY と同じ働き
#                           正規表現を指定すると、他のデコーダにヒットせず、
#                           正規表現にマッチするときに反応
#                           ・・・なのだが、正規表現を指定するとエラーになる？

# message.reply('string')   @発言者名: string でメッセージを送信
# message.send('string')    string を送信
# message.react('icon_emoji')  発言者のメッセージにリアクション(スタンプ)する
#                               文字列中に':'はいらない


# 物体認識モデルの定義

# 動画読み込みの開始
@listen_to(r'^venom,(.*)$')
@listen_to(r'^v,(.*)$')
def start_venom( message , dics ):
    message.reply('実行中')

    response = requests.get(
        'http://0.0.0.0:3000/',
        params={'movie_path': dics })
    message.reply( 'できたよ' )
