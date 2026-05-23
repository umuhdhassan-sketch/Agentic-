import logging
import os
import contextlib
from fastapi import FastAPI, Request
from groq import Groq
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Sanya lambobin sirri
GROQ_API_KEY = "Gsk_P4Gp6Vcfjcc9NcGXYDSDWGdyb3FYXi5lbYB3W65Xo4MREQD2bOue"
TELEGRAM_BOT_TOKEN = "8990797862:AAHey5yxI-YWJtMjOvimfJc7GFSsRTkC57c"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
client = Groq(api_key=GROQ_API_KEY)

# Kaddamar da Telegram Application
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

# Sanya Handlers
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

# Sabon tsarin Lifespan na FastAPI
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    await bot_app.initialize()
    await bot_app.bot.set_webhook(url="https://agentic-markets.onrender.com/webhook")
    await bot_app.start()
    logging.info("🚀 Bot Webhook successfully initialized!")
    yield
    await bot_app.stop()
    await bot_app.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def index():
    return {"status": "AgenticMarkets Bot is Running"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"status": "ok"}
    
