import os
import json
import asyncio
from urllib.request import urlopen
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from flask import Flask, request


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hello! I am your bot. Send /joke for a joke or type a message and I will echo it back."
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    await update.message.reply_text(f"You said: {user_message}")

async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with urlopen("https://official-joke-api.appspot.com/random_joke", timeout=10) as response:
        joke_data = json.loads(response.read().decode("utf-8"))
    await update.message.reply_text(f"{joke_data['setup']}... {joke_data['punchline']}")


app = Flask(__name__)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Set TELEGRAM_BOT_TOKEN")

RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "").strip().rstrip("/")
USE_WEBHOOK = RENDER_EXTERNAL_URL.startswith(("http://", "https://"))
WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}/{TOKEN}" if USE_WEBHOOK else None

application = Application.builder().token(TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("joke", joke))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    loop.run_until_complete(application.process_update(update))
    return "ok"


@app.route("/")
def home():
    return "Bot is running!"



if __name__ == "__main__":
    if USE_WEBHOOK:
        async def setup():
            await application.initialize()
            await application.start()
            await application.bot.set_webhook(WEBHOOK_URL)

        loop.run_until_complete(setup())

        port = int(os.environ.get("PORT", 10000))
        app.run(host="0.0.0.0", port=port)
    else:
        print("RENDER_EXTERNAL_URL is not set to a valid http/https URL. Starting in polling mode.")
        application.run_polling()