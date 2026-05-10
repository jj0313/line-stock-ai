from flask import Flask, request
import requests
import os

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = "bKv3n4K3Dbgw+budYmHIIQzkEsv/zilPtqOVel1fscSwucLENA9yJUctrcLOgG6yVQdC/34DGsjV+VhmfkpOm89v+1ZswXS9xwgnadiivyJeq5/Ve3qCE75Guk8XMs1QOai1jhD4HAETn/Ivg5uqoAdB04t89/1O/w1cDnyilFU="

@app.route("/")
def home():
    return "LINE Stock AI is running!"

@app.route("/callback", methods=['POST'])
def callback():

    body = request.json

    events = body.get('events', [])

    for event in events:

        if event['type'] == 'message':

            user_message = event['message']['text']
            reply_token = event['replyToken']

            reply_message(reply_token, f"你剛剛說：{user_message}")

    return 'OK'

def reply_message(reply_token, text):

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }

    data = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ]
    }

    requests.post(
        "https://api.line.me/v2/bot/message/reply",
        headers=headers,
        json=data
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
