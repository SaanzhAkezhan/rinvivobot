# currency_savings_bot.py

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import json
import os

# Хранилище данных (в файле)
DATA_FILE = "savings_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот для учёта валютных сбережений. Используй /add, /balance, /forecast")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user_id = str(update.effective_user.id)

    try:
        currency, amount, rate = context.args
        amount = float(amount)
        rate = float(rate)
    except:
        await update.message.reply_text("Используй формат: /add USD 100 480")
        return

    if user_id not in data:
        data[user_id] = []

    data[user_id].append({
        "currency": currency.upper(),
        "amount": amount,
        "rate": rate
    })
    save_data(data)
    await update.message.reply_text(f"Добавлено: {amount} {currency.upper()} по курсу {rate}")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user_id = str(update.effective_user.id)

    if user_id not in data or not data[user_id]:
        await update.message.reply_text("Пока ничего не добавлено. Используй /add")
        return

    holdings = {}
    for entry in data[user_id]:
        c = entry["currency"]
        holdings[c] = holdings.get(c, 0) + entry["amount"]

    response = "\u2709\ufe0f Текущий баланс:\n"
    for cur, amt in holdings.items():
        response += f"{cur}: {amt:.2f}\n"
    await update.message.reply_text(response)

async def forecast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user_id = str(update.effective_user.id)
    rates = {"USD": 480, "EUR": 510, "CNY": 65}  # текущие курсы
    forecast_rate = 1.03  # 3% доход
    kurs_growth = 1.10    # курс вырастет на 10%

    if user_id not in data or not data[user_id]:
        await update.message.reply_text("Нет данных для прогноза. Добавь их с помощью /add")
        return

    total = 0
    for entry in data[user_id]:
        cur = entry["currency"]
        amt = entry["amount"] * forecast_rate
        total += amt * rates.get(cur, 1) * kurs_growth

    await update.message.reply_text(f"\ud83d\udcca Прогноз на год: ~ {total:.0f} тенге")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user_id = str(update.effective_user.id)
    if user_id in data:
        data[user_id] = []
        save_data(data)
        await update.message.reply_text("\u274c Все данные удалены")
    else:
        await update.message.reply_text("Нет данных для удаления")

# Основной запуск
app = ApplicationBuilder().token("8148367012:AAGLl9ggsm-gPUccitdNWGtKKv9QK_AesdU").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("forecast", forecast))
app.add_handler(CommandHandler("reset", reset))

if __name__ == '__main__':
    print("Бот запущен...")
    app.run_polling()
