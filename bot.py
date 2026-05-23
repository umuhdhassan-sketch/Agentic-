from telegram.ext import Application, MessageHandler, filters
from groq import Groq
import logging

# Sanya lambobin sirri
TOKEN = "8990797862:AAHey5yxI-YWJtMjOvimfJc7GFSsRTkC57c"
GROQ_API = "Gsk_P4Gp6Vcfjcc9NcGXYDSDWGdyb3FYXi5lbYB3W65Xo4MREQD2bOue"
client = Groq(api_key=GROQ_API)

async def reply(update, context):
    user_text = update.message.text
    # Amsa da Groq
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": user_text}],
        model="llama3-8b-8192"
    )
    ai_reply = chat_completion.choices[0].message.content
    await update.message.reply_text(ai_reply)

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    print("Bot yana gudu... yana sauraron saƙonni!")
    app.run_polling()
    
