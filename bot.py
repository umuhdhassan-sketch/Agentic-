import logging
import os
import asyncio
from aiohttp import web
from groq import Groq
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Sanya lambobin sirri
GROQ_API_KEY = "Gsk_P4Gp6Vcfjcc9NcGXYDSDWGdyb3FYXi5lbYB3W65Xo4MREQD2bOue"
TELEGRAM_BOT_TOKEN = "8990797862:AAHey5yxI-YWJtMjOvimfJc7GFSsRTkC57c"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
client = Groq(api_key=GROQ_API_KEY)

# Kaddamar da Telegram Bot Application
bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

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

# Sanya Handlers na Bot din
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

# Kare bukatun Render Free (Health Check API)
async def handle_health(request):
    return web.Response(text="OK", content_type="text/plain")

async def main():
    # 1. Kaddamar da aiohttp Web Server a cikin asyncio loop guda daya
    server_app = web.Application()
    server_app.router.add_get('/', handle_health)
    
    runner = web.AppRunner(server_app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"🚀 Health Server dynamically tied to port {port}")

    # 2. Fara amfani da tsarin Polling na Telegram a cikin loop din lafiya lau
    async with bot_app:
        await bot_app.initialize()
        await bot_app.start()
        await bot_app.updater.start_polling()
        logging.info("🚀 Telegram Bot is polling smoothly in harmony with the web server...")
        
        # Tsayawa a kunne har abada
        while True:
            await asyncio.sleep(3600)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
        
