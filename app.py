from flask import Flask, request, abort
import os

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import gspread
import json
import random

#ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成
from oauth2client.service_account import ServiceAccountCredentials 

#2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

#認証情報設定
#ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
credentials = ServiceAccountCredentials.from_json_keyfile_name(os.environ[apiKey], scope)

#OAuth2の資格情報を使用してGoogle APIにログイン
gs = gspread.authorize(credentials)

#共有設定したスプレッドシートキーを変数[SPREADSHEET_KEY]に格納する。
SPREADSHEET_KEY = '1gMvKboqdyOrl2g9_pEpsgFAlEnCKkS70eiggn6e3BG8'

#共有設定したスプレッドシートのsheet1を開く
worksheet = gs.open_by_key(SPREADSHEET_KEY).worksheet("sheet1")


app = Flask(__name__)

line_bot_api = LineBotApi('/EF+GGjKrbIUq9ph5Wt2XiyPLmT3+3aBpYNRFESKIWA2Pxq+HnlsiuSoqd9pjZGtnSjq9D53Om+9W0wU9SFzyk5piqhxGYtwit+eySTn7u18jdOiTfY2Hz65P6NyJrTMhYZ+GdpJKED+y1RCy7kXVAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('76c1a65f62b652e9e942b1b1a3efb7ce')

@app.route("/")
def test():
    return "OK"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #ーとか!を除いた最後の文字の位置を調べる
    k = -1
    count = 1
    array = ["あ","い","う","え","お","か","き","く","け","こ","さ","し","す","せ","そ","た","ち","つ","て","と","な","に","ぬ","ね","の","は","ひ","ふ","へ","ほ","ま","み","む","め","も","や","ゆ","よ","ら","り","る","れ","ろ","わ"]
    for i in range(-1,-len(event.message.text),-1):
        if event.message.text[i] == "ー":
            k -= 1
        elif event.message.text[i] == "-":
            k -= 1
        elif event.message.text[i] == "!":
            k -= 1
        elif event.message.text[i] == "！":
            k -= 1
        elif event.message.text[i] == "？":
            k -= 1
        elif event.message.text[i] == "?":
            k -= 1
        elif event.message.text[i] == "～":
            k -= 1
        elif event.message.text[i] == "~":
            k -= 1
        else:
            break

    #相手の最後の文字が「ん」だったとき相手の負け
    if event.message.text[k] == "ん":
        reply_message1 = "キミノマケメカ"
        reply_message2 = "デナオシテコイメカ"
        line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text=reply_message1),TextSendMessage(text=reply_message2)])

    #「ん」意外の時最後の文字からはじまる曲名をランダムで出力する
    else:
        x = random.randint(2,99) #ランダムな曲名を出力するときに使う
        endchar = event.message.text[k]
        endchar = endchar.replace("が","か").replace("ぎ","き").replace("ぐ","く").replace("げ","け").replace("ご","こ").replace("ざ","さ").replace("じ","し").replace("ず","す").replace("ぜ","せ").replace("ぞ","そ").replace("だ","た").replace("ぢ","ち").replace("づ","つ").replace("で","て").replace("ど","と").replace("ば","は").replace("び","ひ").replace("ぶ","ふ").replace("べ","へ").replace("ぼ","ほ").replace("ぱ","は").replace("ぴ","ひ").replace("ぷ","ふ").replace("ぺ","へ").replace("ぽ","ほ").replace("ぁ","あ").replace("ぃ","い").replace("ぅ","う").replace("ぇ","え").replace("ぉ","お").replace("っ","つ").replace("ゃ","や").replace("ゅ","ゆ").replace("ょ","よ").replace("ゎ","わ").replace("ゔ","う").replace("を","お")
        #最後の文字と同じ文字を一列目から探す
        for i in range(0,44):
            if endchar == array[i]:
                break
            else:
                count += 1

        #最後の文字と同じ文字があった時
        if count < 45:
            myendchar = worksheet.cell(count,x).value[-1]
            reply_message1 = worksheet.cell(count,x).value
            #自分の文字の最後が「ん」だったとき自分の負け
            if myendchar == "ん":
                reply_message2 = "ワタシノマケメカ"
                line_bot_api.reply_message(
                    event.reply_token,
                    [TextSendMessage(text=reply_message1),TextSendMessage(text=reply_message2)])
            #自分の最後の文字が「ん」意外だった時曲名を出力
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=reply_message1))
        #最後の文字と同じ文字がなかった時
        else:
            reply_message = "ソンナキョクハナイメカ"
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_message))


if __name__ == "__main__":
    app.run()
