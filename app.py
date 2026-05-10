from flask import Flask, request
import requests
import os
import google.generativeai as genai

app = Flask(__name__)

# ===================================
# 環境變數
# ===================================

CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print("LINE TOKEN 是否存在：", CHANNEL_ACCESS_TOKEN is not None)
print("GEMINI KEY 是否存在：", GEMINI_API_KEY is not None)

# ===================================
# Gemini 初始化
# ===================================

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-pro")

# ===================================
# 首頁
# ===================================

@app.route("/")
def home():
    return "LINE Stock AI is running!"

# ===================================
# LINE Webhook
# ===================================

@app.route("/callback", methods=["POST"])
def callback():

    try:

        body = request.json

        print("========== 收到 webhook ==========")
        print(body)

        events = body.get("events", [])

        for event in events:

            if event["type"] == "message":

                if event["message"]["type"] == "text":

                    user_message = event["message"]["text"]
                    reply_token = event["replyToken"]

                    print("使用者訊息：", user_message)

                    # ===================================
                    # Gemini AI
                    # ===================================

                    try:

                        prompt = f"""
你是一位專業台股分析師。

請針對以下問題進行專業分析：

{user_message}
"""

                        response = model.generate_content(prompt)

                        print("========== Gemini 回覆 ==========")
                        print(response)

                        ai_reply = "AI 沒有成功產生內容"

                        try:

                            if response.text:
                                ai_reply = response.text[:1000]

                        except Exception as text_error:

                            print("讀取 response.text 錯誤")
                            print(text_error)

                            ai_reply = "AI 回覆格式異常"

                    except Exception as gemini_error:

                        print("========== GEMINI ERROR ==========")
                        print(gemini_error)
                        print("==================================")

                        ai_reply = f"Gemini 錯誤：{str(gemini_error)}"

                    # ===================================
                    # 回覆 LINE
                    # ===================================

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

                    print("========== 準備回覆 LINE ==========")
                    print(data)

                    response_line = requests.post(
                        "https://api.line.me/v2/bot/message/reply",
                        headers=headers,
                        json=data
                    )

                    print("========== LINE API RESPONSE ==========")
                    print("狀態碼:", response_line.status_code)
                    print("內容:", response_line.text)
                    print("======================================")

        return "OK"

    except Exception as callback_error:

        print("========== CALLBACK ERROR ==========")
        print(callback_error)
        print("====================================")

        return "ERROR"

# ===================================
# 主程式
# ===================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
