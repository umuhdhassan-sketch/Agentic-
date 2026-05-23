from telegram.ext import Application, CommandHandler, MessageHandler, filters
from groq import Groq
import os

# Lambobin sirri
TOKEN = "8990797862:AAHey5yxI-YWJtMjOvimfJc7GFSsRTkC57c"
GROQ_API = "Gsk_P4Gp6Vcfjcc9NcGXYDSDWGdyb3FYXi5lbYB3W65Xo4MREQD2bOue"
client = Groq(api_key=GROQ_API)

async def start(update, context):
    await update.message.reply_text("AgenticMarkets Bot yana aiki!")

async def reply(update, context):
    msg = update.message.text
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": msg}],
        model="llama3-8b-8192"
    )
    await update.message.reply_text(chat_completion.choices[0].message.content)

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, reply))
    print("Bot yana aiki...")
    app.run_polling()
    
