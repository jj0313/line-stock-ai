from flask import Flask, request
import requests
import os
import google.generativeai as genai

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

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    system_instruction="""
你是一位專業台股投資分析師。

你擅長：
- 台股分析
- 技術分析
- KD 指標
- 布林通道
- 均線
- 成交量
- 短線交易
- 波段交易

請用專業且容易理解的方式回答。
"""
)

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

                    # 預設回覆
                    ai_reply = "AI 暫時無法回覆"

                    try:

                        # =========================
                        # Gemini 回覆
                        # =========================

                        response = model.generate_content(user_message)

                        print("Gemini 回覆成功")

                        if response.text:
                            ai_reply = response.text[:1000]

                    except Exception as e:

                        print("========== GEMINI ERROR ==========")
                        print(e)
                        print("==================================")

                        ai_reply = f"系統提示：目前無法取得 AI 回覆，請稍後再試。({str(e)})"

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

                    # 發送 LINE 回覆
                    line_res = requests.post(
                        "https://api.line.me/v2/bot/message/reply",
                        headers=headers,
                        json=data
                    )

                    # Log
                    if line_res.status_code != 200:

                        print("========== LINE ERROR ==========")
                        print("狀態碼：", line_res.status_code)
                        print("內容：", line_res.text)
                        print("================================")

                    else:

                        print("LINE 回覆成功！")

        return "OK"

    except Exception as e:

        print("========== CALLBACK ERROR ==========")
        print(e)
        print("====================================")

        return "ERROR"

# =========================
# 主程式
# =========================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
