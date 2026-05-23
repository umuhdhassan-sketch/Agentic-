import os
import requests
from flask import Flask, request
from groq import Groq

app = Flask(__name__)

# Lambobin sirri
GROQ_API_KEY = "Gsk_P4Gp6Vcfjcc9NcGXYDSDWGdyb3FYXi5lbYB3W65Xo4MREQD2bOue"
TELEGRAM_BOT_TOKEN = "8990797862:AAHey5yxI-YWJtMjOvimfJc7GFSsRTkC57c"
RENDER_URL = "https://agentic--markets.onrender.com"

client = Groq(api_key=GROQ_API_KEY)

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
        return "Sorry, I encountered an issue."

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.route('/', methods=['GET'])
def index():
    return "AgenticMarkets Bot is Live on Flask!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]
        
        # Nuna cewa bot yana rubutu
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendChatAction", json={"chat_id": chat_id, "action": "typing"})
        
        if user_text.strip() == '/start':
            send_message(chat_id, "Hello! AgenticMarkets AI Bot is officially online via Flask Webhook!")
        else:
            reply = ask_groq(user_text)
            send_message(chat_id, reply)
            
    return "OK", 200

if __name__ == '__main__':
    # Hada Telegram da Render
    webhook_url = f"{RENDER_URL}/webhook"
    requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={webhook_url}")
    
    # Kaddamar da Flask akan Port din Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
