from flask import Flask, request
import requests
import os
from openai import OpenAI

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = "QBl2dH/ogltdFZs4aXtgm+wl+z6L1voQTV6THuTWpD6PH16e4if2OaubTTg7CaRDVQdC/34DGsjV+VhmfkpOm89v+1ZswXS9xwgnadiivyIiHzGn7YgrZiqOoL1kHLUWg0oja3FjxULyStLAQnyweQdB04t89/1O/w1cDnyilFU="

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

@app.route("/")
def home():
    return "LINE Stock AI is running!"

@app.route("/callback", methods=["POST"])
def callback():

    body = request.json

    events = body.get("events", [])

    for event in events:

        if event["type"] == "message":

            user_message = event["message"]["text"]

            reply_token = event["replyToken"]

            # GPT 回覆
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位專業台股投資分析師"
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )

            ai_reply = response.choices[0].message.content

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
            }

            data = {
                "replyToken": reply_token,
                "messages": [
                    {
                        "type": "text",
                        "text": ai_reply
                    }
                ]
            }

            requests.post(
                "https://api.line.me/v2/bot/message/reply",
                headers=headers,
                json=data
            )

    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
