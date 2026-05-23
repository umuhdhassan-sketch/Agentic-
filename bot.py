import logging
import os
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from groq import Groq
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Sanya lambobin sirri
GROQ_API_KEY = "Gsk_P4Gp6Vcfjcc9NcGXYDSDWGdyb3FYXi5lbYB3W65Xo4MREQD2bOue"
TELEGRAM_BOT_TOKEN = "8990797862:AAHey5yxI-YWJtMjOvimfJc7GFSsRTkC57c"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
client = Groq(api_key=GROQ_API_KEY)

# Server ta karya don baiwa Render amsa nan take
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        return  # Kashe logs din server don kar su cika allo

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    logging.info(f"Health server running on port {port}")
    server.serve_forever()

def ask_groq(user_text):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a professional AI assistant. Respond in English only."},
                {"role": "user", "content": user_text}
            ],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Groq API Error: {e}")
        return "Sorry, I encountered an issue. Please try again."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Your AgenticMarkets AI Bot is officially online 24/7 on Render Free. Ask me anything!")

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    ai_answer = ask_groq(user_message)
    await update.message.reply_text(ai_answer)

async def main():
    # Kunna server din Render a bango ta amfani da Threading
    threading.Thread(target=run_health_server, daemon=True).start()
    
    # Kaddamar da Telegram Bot
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    
    # Kunna tsarin Polling na gaskiya
    async with app:
        await app.initialize()
        await app.start()
        print("🚀 Bot is successfully polling Telegram...")
        await app.updater.start_polling()
        # Tsayawa a kunne har abada
        while True:
            await asyncio.sleep(3600)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
        
