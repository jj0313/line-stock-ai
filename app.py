# =========================
# 回覆 LINE (優化版)
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

# 發送請求
line_res = requests.post(
    "https://api.line.me/v2/bot/message/reply",
    headers=headers,
    json=data
)

# 在 Log 記錄狀態，方便除錯
if line_res.status_code != 200:
    print(f"LINE 回覆失敗！狀態碼：{line_res.status_code}, 原因：{line_res.text}")
else:
    print("LINE 回覆成功！")
