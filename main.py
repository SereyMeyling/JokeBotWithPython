import os
import json
from urllib.request import urlopen
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

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

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()



def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Set the TELEGRAM_BOT_TOKEN environment variable before running the bot.")

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("joke", joke))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    threading.Thread(target=run_dummy_server).start()
    application.run_polling()


if __name__ == "__main__":
    main()
