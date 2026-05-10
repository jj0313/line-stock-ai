from flask import Flask, request
import requests
import os
import google.generativeai as genai

app = Flask(__name__)

# --- 設定區 ---
# 請確保你在 Render 的 Environment Variables 裡設定了這兩個 Key
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "你的_LINE_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 初始化 Gemini
genai.configure(api_key=GEMINI_API_KEY)

# 設定模型，並將「專業台股分析師」的角色設定放在這裡
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", # flash 版本速度快且免費額度高
    system_instruction="你是一位專業台股投資分析師，請用專業且親切的語氣回覆使用者。"
)

@app.route("/")
def home():
    return "LINE Stock AI (Gemini Edition) is running!"

@app.route("/callback", methods=["POST"])
def callback():
    body = request.json
    events = body.get("events", [])

    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            user_message = event["message"]["text"]
            reply_token = event["replyToken"]

            try:
                # Gemini 生成回覆
                response = model.generate_content(user_message)
                ai_reply = response.text
            except Exception as e:
                print(f"Gemini Error: {e}")
                ai_reply = "抱歉，我現在大腦稍微打結了，請稍後再試。"

            # LINE 回覆邏輯
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
    # Render 會自動給予 PORT 環境變數，若無則預設 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
