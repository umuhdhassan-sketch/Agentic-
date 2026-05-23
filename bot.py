import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from groq import Groq
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Sanya lambobin sirri
GROQ_API_KEY = "Gsk_P4Gp6Vcfjcc9NcGXYDSDWGdyb3FYXi5lbYB3W65Xo4MREQD2bOue"
TELEGRAM_BOT_TOKEN = "8990797862:AAHey5yxI-YWJtMjOvimfJc7GFSsRTkC57c"
RENDER_URL = "https://agentic-w7gr.onrender.com"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
client = Groq(api_key=GROQ_API_KEY)

# Kaddamar da Telegram Application
app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

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
    await update.message.reply_text("Hello! Your AgenticMarkets AI Bot is officially online 24/7 via Webhook. Ask me anything!")

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    ai_answer = ask_groq(user_message)
    await update.message.reply_text(ai_answer)

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

# Sabar HTTP wacce za ta karbi sakonni kai tsaye daga Telegram
class WebhookHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Health check na Render
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running")

    def do_POST(self):
        # Karbar sakonni daga Telegram
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            update_json = json.loads(post_data.decode('utf-8'))
            update = Update.de_json(update_json, app.bot)
            
            # Gudanar da sakon a cikin asalin loop na telegram
            import asyncio
            asyncio.run(app.process_update(update))
        except Exception as e:
            logging.error(f"Error processing update: {e}")

        self.send_response(200)
        self.end_headers()

def main():
    # Kunna Webhook a sabar Telegram da kanta
    import asyncio
    asyncio.run(app.bot.set_webhook(url=f"{RENDER_URL}/webhook"))
    logging.info("🚀 Webhook successfully registered with Telegram!")

    # Fara sabar HTTP akan Port na Render
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), WebhookHandler)
    logging.info(f"🚀 Webhook Server listening on port {port}")
    server.serve_forever()

if __name__ == '__main__':
    main()
