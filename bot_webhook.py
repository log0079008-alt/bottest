import os
from flask import Flask, request
import requests
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- Настройки ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # добавь BOT_TOKEN как переменную среды на Render
SPREADSHEET_URL = os.environ.get("SPREADSHEET_URL")  # тоже переменная среды

# Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open_by_url(SPREADSHEET_URL).sheet1

# Flask
app = Flask(__name__)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        if text == "Я на месте ✅":
            name = message["from"].get("first_name", "") + " " + message["from"].get("last_name", "")
            user_id = message["from"]["id"]
            time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([name, str(user_id), time_now])
            send_message(chat_id, "✅ Отметка сохранена!")
        else:
            send_message(chat_id, "Привет! Нажми кнопку 'Я на месте ✅' для отметки.")

    return {"ok": True}

@app.route("/")
def index():
    return "Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
