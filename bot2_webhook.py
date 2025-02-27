import requests
import telegram
from flask import Flask, request

# 🔹 اطلاعات بات ۲ و متیس
TOKEN_BOT_2 = "tpsg-mPgpjyrDBiFEW8dlzQ4e4Uve2oOfFvB"  # توکن API بات ۲ در تلگرام
API_METIS = "https://api.metisai.ir/api/v1"
API_KEY = "tpsg-mPgpjyrDBiFEW8dlzQ4e4Uve2oOfFvB"
BOT_ID = "86e25937-7a57-4238-aea1-d4af8bbd8fc4"

# 🔹 تنظیمات تلگرام
bot = telegram.Bot(token=TOKEN_BOT_2)
app = Flask(__name__)

# 🔹 هدرهای درخواست برای متیس
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 🔹 دریافت پیام از تلگرام و پردازش
@app.route(f"/{TOKEN_BOT_2}", methods=["POST"])
def webhook():
    data = request.get_json()
    
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]

        # ۱. ایجاد گفت‌وگو در متیس
        conversation_id = create_conversation()
        if not conversation_id:
            bot.send_message(chat_id=chat_id, text="⛔ خطا در ارتباط با سرور!")
            return "Error", 500
        
        # ۲. ارسال پیام به بات متیس
        send_message(conversation_id, text)
        
        # ۳. دریافت پاسخ از متیس
        messages = get_messages(conversation_id)
        if messages:
            bot_reply = next((msg['text'] for msg in messages if msg['sender'] == "bot"), "⛔ پاسخ موجود نیست!")
            bot.send_message(chat_id=chat_id, text=bot_reply)
        else:
            bot.send_message(chat_id=chat_id, text="⛔ خطا در دریافت پاسخ!")

    return "OK", 200

# 🔹 توابع ارتباط با متیس
def create_conversation():
    url = f"{API_METIS}/conversations"
    data = {"botId": BOT_ID, "title": "New Conversation"}
    response = requests.post(url, json=data, headers=headers)
    return response.json().get("id") if response.ok else None

def send_message(conversation_id, message):
    url = f"{API_METIS}/conversations/{conversation_id}/messages"
    data = {"text": message}
    requests.post(url, json=data, headers=headers)

def get_messages(conversation_id):
    url = f"{API_METIS}/conversations/{conversation_id}/messages"
    response = requests.get(url, headers=headers)
    return response.json() if response.ok else None

# اجرای سرور
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
