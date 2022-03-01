from os import popen
from linebot import LineBotApi
from linebot.models import TextSendMessage, FlexSendMessage
from Frontend.functions import get_secret
from json import loads

# https://github.com/line/line-bot-sdk-python

KEYS = loads(get_secret("my-messenger"))

def get_client(target="Cloud"):
    if target == "YYY":
        return LineBotApi(KEYS["LINE-YYY"])
    else:
        return LineBotApi(KEYS["LINE-MSG"])

def send_line(target="cloud", text="Hello", flex=None):
    # LINE_API.push_message('<to>', TextSendMessage(text='Hello World!'))
    try:
        if flex == None:
            get_client().broadcast(TextSendMessage(text=text))
        else:
            get_client().broadcast(FlexSendMessage(alt_text=text,contents=flex))
    except Exception as e:
        print(str(e))


def check_consumption():
    tmpkey = KEYS["LINE-MSG"] if 1==0 else KEYS["LINE-YYY"]
    popen(f"curl -v -X GET https://api.line.me/v2/bot/message/quota/consumption -H 'Authorization: Bearer {tmpkey}'").read()

