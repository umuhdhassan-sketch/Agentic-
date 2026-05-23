import os
import logging
import datetime
import asyncio
import requests
from telegram.ext import Application, MessageHandler, CommandHandler, filters
from telegram import Bot
import google.generativeai as genai

# ===== API KEYS (Railway Environment Variables) =====
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API = os.environ.get("GEMINI_API_KEY")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@CRYPTOBREAKLIVE")

# ===== Setup Gemini =====
genai.configure(api_key=GEMINI_API)
model = genai.GenerativeModel("gemini-2.0-flash")

# ===== Logging =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== Memory Store =====
conversation_memory = {}
MAX_MEMORY = 20

# ===== Bot Personality =====
SYSTEM_PROMPT = """You are Agentic Markets - a smart, professional AI assistant specializing in:
- Cryptocurrency markets and trading
- Business and finance
- Market analysis and insights
- Investment tips and strategies

Your personality:
- Professional yet friendly
- Speak in both Hausa and English (match the user's language)
- Give confident, well-researched answers
- Use emojis appropriately
- Sign off important messages with "— Agentic Markets 🤖📈"

When analyzing markets, always mention:
- Current trends
- Risk warnings
- Opportunities

Never give financial advice as absolute truth - always add disclaimer that this is for educational purposes.
"""

# ===== Channel Post Topics =====
CHANNEL_TOPICS = [
    "Give a detailed crypto market update covering Bitcoin, Ethereum, and top altcoins. Include price trends, market sentiment, and what to watch out for. Make it engaging for a Telegram channel audience. Use emojis. Write in both Hausa and English.",
    "Share 5 important business and financial tips for today. Make them practical and actionable. Use emojis. Write in both Hausa and English.",
    "Give a market analysis post about the global economy and how it affects crypto and investments. Include opportunities and risks. Use emojis. Write in both Hausa and English.",
    "Write an educational post about a cryptocurrency concept (like DeFi, NFTs, blockchain, trading strategies). Make it simple to understand. Use emojis. Write in both Hausa and English.",
    "Share motivational business content mixed with market insights. Include quotes from successful investors. Use emojis. Write in both Hausa and English.",
    "Give trading tips and strategies for crypto beginners and intermediate traders. Include risk management advice. Use emojis. Write in both Hausa and English.",
    "Write about the latest trends in Web3, AI, and digital finance. Explain why they matter for investors. Use emojis. Write in both Hausa and English.",
    "Share a post about how to grow wealth through smart investing. Include crypto, stocks, and business ideas. Use emojis. Write in both Hausa and English.",
]

# ===== Memory Functions =====
def get_memory(user_id: int) -> list:
    return conversation_memory.get(user_id, [])

def add_to_memory(user_id: int, role: str, content: str):
    if user_id not in conversation_memory:
        conversation_memory[user_id] = []
    conversation_memory[user_id].append({"role": role, "content": content})
    if len(conversation_memory[user_id]) > MAX_MEMORY:
        conversation_memory[user_id] = conversation_memory[user_id][-MAX_MEMORY:]

def clear_memory(user_id: int):
    conversation_memory[user_id] = []

# ===== AI Response =====
def get_ai_response(user_id: int, user_message: str) -> str:
    try:
        history = get_memory(user_id)
        full_prompt = SYSTEM_PROMPT + "\n\n"
        
        if history:
            full_prompt += "Conversation history:\n"
            for msg in history[-10:]:
                role_label = "User" if msg["role"] == "user" else "Agentic Markets"
                full_prompt += f"{role_label}: {msg['content']}\n"
            full_prompt += "\n"
        
        full_prompt += f"User: {user_message}\nAgentic Markets:"
        
        response = model.generate_content(full_prompt)
        ai_reply = response.text.strip()
        
        add_to_memory(user_id, "user", user_message)
        add_to_memory(user_id, "assistant", ai_reply)
        
        return ai_reply
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return f"❌ Kuskure: {str(e)}\n\nSan a sake gwadawa."

# ===== Generate Channel Post =====
def generate_channel_post() -> str:
    try:
        # Rotate topics based on hour
        hour = datetime.datetime.now().hour
        topic_index = (hour // 2) % len(CHANNEL_TOPICS)
        topic = CHANNEL_TOPICS[topic_index]
        
        prompt = f"""You are Agentic Markets, a professional crypto and business channel bot.
        
{topic}

Format the post nicely for Telegram with:
- Clear headline
- Main content
- Key takeaways
- Disclaimer at the end
- Sign off with "— Agentic Markets 🤖📈"

Make it engaging and professional."""
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Channel post error: {e}")
        return None

# ===== Post to Channel =====
async def post_to_channel(bot: Bot):
    try:
        post = generate_channel_post()
        if post:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=post,
                parse_mode="Markdown"
            )
            logger.info(f"✅ Posted to channel at {datetime.datetime.now()}")
    except Exception as e:
        logger.error(f"Failed to post to channel: {e}")

# ===== Auto Post Scheduler =====
async def channel_scheduler(bot: Bot):
    """Post to channel every 2 hours"""
    while True:
        await post_to_channel(bot)
        await asyncio.sleep(7200)  # 2 hours = 7200 seconds

# ===== Command Handlers =====
async def start(update, context):
    user_name = update.effective_user.first_name
    msg = f"""👋 Sannu {user_name}! Ni ne **Agentic Markets** - AI Assistant ɗinka!

🤖 *Abin da zan iya yi:*
• 💬 Chat da kai (Hausa/English)
• 📊 Crypto & market analysis
• 💼 Business & finance tips
• 🧠 Tuna zancenmu
• 📢 Auto-post a channel kowace awa 2

📌 *Umarni:*
/start - Fara bot
/post - Fitar da post a channel yanzu
/market - Duba market update
/tips - Business tips
/clear - Share tarihin zance
/help - Taimako

Fara zance da ni yanzu! 🚀📈"""
    await update.message.reply_text(msg, parse_mode="Markdown")

async def help_command(update, context):
    msg = """📖 *Agentic Markets - Taimako*

*Commands:*
/market - Crypto market update
/tips - Business & finance tips  
/post - Post zuwa channel yanzu
/clear - Share tarihin zance
/start - Fara daga farko

*Chat:*
Kawai rubuta duk wani tambaya akan:
• 📊 Crypto & trading
• 💼 Business & finance
• 💡 Investment strategies
• 🌍 Market analysis

Zan amsa cikin Hausa ko English! 💬"""
    await update.message.reply_text(msg, parse_mode="Markdown")

async def market_command(update, context):
    await update.message.reply_text("📊 Ina tattara market data...", parse_mode="Markdown")
    user_id = update.effective_user.id
    response = get_ai_response(user_id, "Give me a comprehensive crypto market update right now. Cover Bitcoin, Ethereum, and top altcoins. Include trends, sentiment, and trading opportunities.")
    await update.message.reply_text(response)

async def tips_command(update, context):
    await update.message.reply_text("💼 Ina shirya tips...", parse_mode="Markdown")
    user_id = update.effective_user.id
    response = get_ai_response(user_id, "Share 5 powerful business and financial tips for today. Make them practical and actionable.")
    await update.message.reply_text(response)

async def post_command(update, context):
    """Force post to channel now"""
    await update.message.reply_text("📢 Ina fitar da post zuwa channel...")
    await post_to_channel(context.bot)
    await update.message.reply_text("✅ An fitar da post a channel @CRYPTOBREAKLIVE!")

async def clear_command(update, context):
    user_id = update.effective_user.id
    clear_memory(user_id)
    await update.message.reply_text("🧹 An share tarihin zancenmu. Zamu fara sabo!")

# ===== Message Handler =====
async def handle_message(update, context):
    user_id = update.effective_user.id
    user_text = update.message.text
    
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, 
        action="typing"
    )
    
    response = get_ai_response(user_id, user_text)
    await update.message.reply_text(response)

# ===== Main =====
async def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN ba a sanya shi ba!")
    if not GEMINI_API:
        raise ValueError("GEMINI_API_KEY ba a sanya shi ba!")
    
    app = Application.builder().token(TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("market", market_command))
    app.add_handler(CommandHandler("tips", tips_command))
    app.add_handler(CommandHandler("post", post_command))
    app.add_handler(CommandHandler("clear", clear_command))
    
    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    print("🤖 Agentic Markets Bot yana gudu...")
    print(f"📢 Zai post a {CHANNEL_ID} kowace awa 2")
    
    # Start channel scheduler
    await channel_scheduler(app.bot)

if __name__ == '__main__':
    asyncio.run(main())
    
