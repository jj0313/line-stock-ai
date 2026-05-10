from flask import Flask, request
import requests
import os

# Gemini

import google.generativeai as genai

# NVIDIA

from openai import OpenAI

app = Flask(**name**)

# =========================

# 環境變數

# =========================

CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

print("LINE TOKEN 是否存在：", CHANNEL_ACCESS_TOKEN is not None)
print("GEMINI KEY 是否存在：", GEMINI_API_KEY is not None)
print("NVIDIA KEY 是否存在：", NVIDIA_API_KEY is not None)

# =========================

# Gemini 初始化

# =========================

if GEMINI_API_KEY:
genai.configure(api_key=GEMINI_API_KEY)

# =========================

# NVIDIA 初始化

# =========================

nvidia_client = None

if NVIDIA_API_KEY:

```
nvidia_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)
```

# =========================

# AI 回覆函式

# =========================

def ask_ai(user_message):

```
# =========================
# 優先 NVIDIA
# =========================

if nvidia_client:

    try:

        print("===== 使用 NVIDIA =====")

        completion = nvidia_client.chat.completions.create(
            model="meta/llama-3.1-70b-instruct",
            messages=[
                {
                    "role": "system",
                    "content": """
```

你是一位專業台股投資分析師。

你擅長：

* 台股分析
* 技術分析
* KD 指標
* 布林通道
* 均線
* 成交量
* 短線交易
* 波段交易

請用專業且容易理解的方式回答。
"""
},
{
"role": "user",
"content": user_message
}
],
temperature=0.2,
top_p=0.7,
max_tokens=512
)

```
        ai_reply = completion.choices[0].message.content

        if ai_reply:

            print("NVIDIA 回覆成功")

            return ai_reply[:1000]

    except Exception as e:

        print("========== NVIDIA ERROR ==========")
        print(e)
        print("==================================")

# =========================
# NVIDIA 失敗 → Gemini
# =========================

if GEMINI_API_KEY:

    try:

        print("===== 切換 Gemini =====")

        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction="""
```

你是一位專業台股投資分析師。

你擅長：

* 台股分析
* 技術分析
* KD 指標
* 布林通道
* 均線
* 成交量
* 短線交易
* 波段交易

請用專業且容易理解的方式回答。
"""
)

```
        response = model.generate_content(user_message)

        ai_reply = ""

        try:
            ai_reply = response.text
        except:
            ai_reply = "Gemini 無法解析回覆"

        if ai_reply:

            print("Gemini 回覆成功")

            return ai_reply[:1000]

    except Exception as e:

        print("========== GEMINI ERROR ==========")
        print(e)
        print("==================================")

# =========================
# 全部失敗
# =========================

return "目前 AI 服務忙碌中，請稍後再試。"
```

# =========================

# 首頁

# =========================

@app.route("/")
def home():

```
return "LINE Stock AI is running!"
```

# =========================

# LINE Callback

# =========================

@app.route("/callback", methods=["POST"])
def callback():

```
try:

    body = request.json

    print("========== 收到 webhook ==========")
    print(body)

    events = body.get("events", [])

    for event in events:

        try:

            if event["type"] == "message":

                if event["message"]["type"] == "text":

                    user_message = event["message"]["text"]

                    reply_token = event["replyToken"]

                    print("使用者訊息：", user_message)

                    # AI 回覆
                    ai_reply = ask_ai(user_message)

                    print("AI 回覆：", ai_reply)

                    # LINE headers
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
                    }

                    # LINE data
                    data = {
                        "replyToken": reply_token,
                        "messages": [
                            {
                                "type": "text",
                                "text": ai_reply
                            }
                        ]
                    }

                    # 發送 LINE
                    line_res = requests.post(
                        "https://api.line.me/v2/bot/message/reply",
                        headers=headers,
                        json=data,
                        timeout=30
                    )

                    print("LINE 狀態碼：", line_res.status_code)
                    print("LINE 回覆：", line_res.text)

        except Exception as e:

            print("========== EVENT ERROR ==========")
            print(e)
            print("=================================")

    return "OK"

except Exception as e:

    print("========== CALLBACK ERROR ==========")
    print(e)
    print("====================================")

    return "ERROR"
```

# =========================

# 主程式

# =========================

if **name** == "**main**":

```
port = int(os.environ.get("PORT", 10000))

app.run(
    host="0.0.0.0",
    port=port
)
```
