from flask import Flask, request
import requests
import os

from google import genai

app = Flask(__name__)

# =========================
# 環境變數
# =========================

CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print("LINE TOKEN 是否存在：", CHANNEL_ACCESS_TOKEN is not None)
print("GEMINI KEY 是否存在：", GEMINI_API_KEY is not None)

# =========================
# Gemini 初始化
# =========================

client = genai.Client(api_key=GEMINI_API_KEY)

# =========================
# 首頁
# =========================

@app.route("/")
def home():
    return "LINE Stock AI is running!"

# =========================
# LINE Webhook
# =========================

@app.route("/callback", methods=["POST"])
def callback():

    body = request.json

    print("收到 webhook")
    print(body)

    events = body.get("events", [])

    for event in events:

        if event["type"] == "message":

            if event["message"]["type"] == "text":

                user_message = event["message"]["text"]
                reply_token = event["replyToken"]

                print("使用者訊息：", user_message)

                try:

                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=f"""
你是一位專業台股投資分析師。

請用專業且容易理解的方式回答。

使用者問題：
{user_message}
"""
                    )

                    ai_reply = response.text[:1000]

                except Exception as e:

                    print("Gemini Error:", e)

                    ai_reply = f"Gemini 錯誤：{str(e)}"

                # =========================
                # 回覆 LINE
                # =========================

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

                response_line = requests.post(
                    "https://api.line.me/v2/bot/message/reply",
                    headers=headers,
                    json=data
                )

                print("LINE 回覆狀態：", response_line.status_code)
                print("LINE 回覆內容：", response_line.text)

    return "OK"

# =========================
# 主程式
# =========================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
