import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from flask import Flask, request, Response
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import os

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
SPREADSHEET_URL = os.environ.get("SPREADSHEET_URL")
CREDS_JSON = "credentials.json"

if not BOT_TOKEN or not SPREADSHEET_URL:
    raise ValueError("Установите BOT_TOKEN и SPREADSHEET_URL в Environment Variables")

# Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(CREDS_JSON, scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open_by_url(SPREADSHEET_URL).sheet1

# Aiogram
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

button_here = types.KeyboardButton("Я на месте ✅")
keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(button_here)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет! 👋 Нажми кнопку, чтобы отметить присутствие.", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "Я на месте ✅")
async def mark_present(message: types.Message):
    name = message.from_user.full_name
    user_id = message.from_user.id
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        sheet.append_row([name, str(user_id), time_now])
        await message.answer("✅ Отметка сохранена!")
    except Exception as e:
        logging.error(f"Ошибка записи в Google Sheets: {e}")
        await message.answer("⚠️ Не удалось сохранить отметку. Попробуй позже.")

# Flask
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dp.loop.create_task(dp.process_update(update))
    return Response("ok", status=200)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))