import os
import logging
import json
import datetime
import requests
from telegram.ext import Application, MessageHandler, CommandHandler, filters
import google.generativeai as genai

# ===== API KEYS (sanya a Railway Environment Variables) =====
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API = os.environ.get("GEMINI_API_KEY")
SEARCH_API = os.environ.get("SEARCH_API_KEY", "")  # Optional: Google Custom Search
SEARCH_CX = os.environ.get("SEARCH_CX", "")        # Optional: Custom Search Engine ID

# ===== Setup Gemini =====
genai.configure(api_key=GEMINI_API)
model = genai.GenerativeModel("gemini-1.5-flash")

# ===== Logging =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== Memory Store (per user) =====
conversation_memory = {}  # {user_id: [{"role": ..., "content": ...}]}
task_store = {}           # {user_id: [{"task": ..., "done": bool, "date": ...}]}

MAX_MEMORY = 20  # Max messages to remember per user

# ===== System Prompt =====
SYSTEM_PROMPT = """You are a smart AI assistant who can speak both Hausa and English.
- If the user writes in Hausa, reply in Hausa.
- If the user writes in English, reply in English.
- You are helpful, friendly, and intelligent.
- You can manage tasks, answer questions, search the web (if asked), and remember conversations.
- When listing tasks, format them clearly and numbered.
- Be concise but complete in your answers.
"""

# ===== Web Search Function =====
def web_search(query: str) -> str:
    """Search the web using Google Custom Search API"""
    if not SEARCH_API or not SEARCH_CX:
        return "Web search ba a kunna shi ba. Sanya SEARCH_API_KEY da SEARCH_CX a environment variables."
    
    try:
        url = f"https://www.googleapis.com/customsearch/v1"
        params = {
            "key": SEARCH_API,
            "cx": SEARCH_CX,
            "q": query,
            "num": 3
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "items" not in data:
            return "Ba a sami sakamakon bincike ba."
        
        results = []
        for item in data["items"][:3]:
            results.append(f"• {item['title']}\n  {item['snippet']}\n  {item['link']}")
        
        return "🔍 Sakamakon bincike:\n\n" + "\n\n".join(results)
    except Exception as e:
        return f"Kuskure wajen bincike: {str(e)}"

# ===== Memory Functions =====
def get_memory(user_id: int) -> list:
    return conversation_memory.get(user_id, [])

def add_to_memory(user_id: int, role: str, content: str):
    if user_id not in conversation_memory:
        conversation_memory[user_id] = []
    conversation_memory[user_id].append({"role": role, "content": content})
    # Keep only last MAX_MEMORY messages
    if len(conversation_memory[user_id]) > MAX_MEMORY:
        conversation_memory[user_id] = conversation_memory[user_id][-MAX_MEMORY:]

def clear_memory(user_id: int):
    conversation_memory[user_id] = []

# ===== Task Functions =====
def add_task(user_id: int, task: str) -> str:
    if user_id not in task_store:
        task_store[user_id] = []
    task_store[user_id].append({
        "task": task,
        "done": False,
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    return f"✅ An ƙara aikin: *{task}*"

def get_tasks(user_id: int) -> str:
    tasks = task_store.get(user_id, [])
    if not tasks:
        return "📋 Ba ka da wani aiki a jerin ka."
    
    result = "📋 *Jerin ayyukanka:*\n\n"
    for i, t in enumerate(tasks, 1):
        status = "✅" if t["done"] else "⏳"
        result += f"{i}. {status} {t['task']} _(_{t['date']}_)_\n"
    return result

def complete_task(user_id: int, task_num: int) -> str:
    tasks = task_store.get(user_id, [])
    if not tasks or task_num < 1 or task_num > len(tasks):
        return "❌ Lambar aiki ba ta dace ba."
    tasks[task_num - 1]["done"] = True
    return f"✅ An kammala aiki #{task_num}: *{tasks[task_num-1]['task']}*"

def delete_task(user_id: int, task_num: int) -> str:
    tasks = task_store.get(user_id, [])
    if not tasks or task_num < 1 or task_num > len(tasks):
        return "❌ Lambar aiki ba ta dace ba."
    removed = tasks.pop(task_num - 1)
    return f"🗑️ An goge aiki: *{removed['task']}*"

# ===== AI Response with Memory =====
def get_ai_response(user_id: int, user_message: str) -> str:
    try:
        # Build conversation history
        history = get_memory(user_id)
        
        # Build full prompt with history
        full_prompt = SYSTEM_PROMPT + "\n\n"
        
        if history:
            full_prompt += "Tarihin zance:\n"
            for msg in history[-10:]:  # Last 10 messages for context
                role_label = "User" if msg["role"] == "user" else "Assistant"
                full_prompt += f"{role_label}: {msg['content']}\n"
            full_prompt += "\n"
        
        full_prompt += f"User: {user_message}\nAssistant:"
        
        response = model.generate_content(full_prompt)
        ai_reply = response.text.strip()
        
        # Save to memory
        add_to_memory(user_id, "user", user_message)
        add_to_memory(user_id, "assistant", ai_reply)
        
        return ai_reply
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return f"❌ Kuskure: {str(e)}\n\nSan a sake gwadawa."

# ===== Command Handlers =====
async def start(update, context):
    user_name = update.effective_user.first_name
    msg = f"""👋 Sannu {user_name}! Ni ne AI Agent ɗinka!

🤖 *Abin da zan iya yi:*
• 💬 Amsa tambayoyinka (Hausa/English)
• 🧠 Tuna zancenmu
• ✅ Manage tasks/ayyuka
• 🔍 Search internet

📌 *Umarni:*
/start - Fara bot
/tasks - Duba ayyukanka
/addtask [aiki] - Ƙara aiki
/donetask [lamba] - Kammala aiki
/deltask [lamba] - Goge aiki
/search [tambaya] - Bincika internet
/clear - Share tarihin zance
/help - Taimako

Fara zance da ni yanzu! 🚀"""
    await update.message.reply_text(msg, parse_mode="Markdown")

async def help_command(update, context):
    msg = """📖 *Taimako / Help*

*Task Management:*
/addtask Sayi kaya - Ƙara aiki
/tasks - Duba duk ayyuka
/donetask 1 - Mark aiki #1 a matsayin done
/deltask 1 - Goge aiki #1

*Search:*
/search latest AI news - Bincika internet

*Memory:*
/clear - Share tarihin zance

*Chat:*
Kawai rubuta duk wani abu - zan amsa! 💬"""
    await update.message.reply_text(msg, parse_mode="Markdown")

async def tasks_command(update, context):
    user_id = update.effective_user.id
    await update.message.reply_text(get_tasks(user_id), parse_mode="Markdown")

async def addtask_command(update, context):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("❌ Rubuta aiki! Misali: /addtask Sayi kaya")
        return
    task = " ".join(context.args)
    await update.message.reply_text(add_task(user_id, task), parse_mode="Markdown")

async def donetask_command(update, context):
    user_id = update.effective_user.id
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❌ Rubuta lambar aiki! Misali: /donetask 1")
        return
    await update.message.reply_text(complete_task(user_id, int(context.args[0])), parse_mode="Markdown")

async def deltask_command(update, context):
    user_id = update.effective_user.id
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❌ Rubuta lambar aiki! Misali: /deltask 1")
        return
    await update.message.reply_text(delete_task(user_id, int(context.args[0])), parse_mode="Markdown")

async def search_command(update, context):
    if not context.args:
        await update.message.reply_text("❌ Rubuta abin da kake nema! Misali: /search latest AI news")
        return
    query = " ".join(context.args)
    await update.message.reply_text("🔍 Ina bincike...", parse_mode="Markdown")
    result = web_search(query)
    await update.message.reply_text(result, parse_mode="Markdown")

async def clear_command(update, context):
    user_id = update.effective_user.id
    clear_memory(user_id)
    await update.message.reply_text("🧹 An share tarihin zancenmu. Zamu fara sabo!")

# ===== Message Handler =====
async def handle_message(update, context):
    user_id = update.effective_user.id
    user_text = update.message.text
    
    # Check if user is asking to search
    lower_text = user_text.lower()
    if any(word in lower_text for word in ["search", "bincika", "google", "find", "nemo"]):
        await update.message.reply_text("🔍 Ina bincike...")
        search_result = web_search(user_text)
        # Give AI the search results to summarize
        combined = f"User asked: {user_text}\n\nSearch results found:\n{search_result}\n\nPlease summarize these results helpfully."
        ai_response = get_ai_response(user_id, combined)
        await update.message.reply_text(ai_response)
        return
    
    # Check if user wants to add a task naturally
    if any(word in lower_text for word in ["add task", "ƙara aiki", "remember to", "remind me to", "tuna mini"]):
        task = user_text
        add_task(user_id, task)
        ai_response = get_ai_response(user_id, f"User wants to remember: {user_text}. Confirm you've noted it.")
        await update.message.reply_text(ai_response)
        return
    
    # Normal AI chat
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    response = get_ai_response(user_id, user_text)
    await update.message.reply_text(response)

# ===== Main =====
if __name__ == '__main__':
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN =8990797862:AAHey5yxI-YWJtMjOvimfJc7GFSsRTkC57c")
    if not GEMINI_API:
        raise ValueError("GEMINI_API_KEY = AIzaSyCqnXKOUIkRUrJ3Iq7__Qx1Igw-CH7ZGOg")
    
    app = Application.builder().token(TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("tasks", tasks_command))
    app.add_handler(CommandHandler("addtask", addtask_command))
    app.add_handler(CommandHandler("donetask", donetask_command))
    app.add_handler(CommandHandler("deltask", deltask_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("clear", clear_command))
    
    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 AI Agent yana gudu...")
    app.run_polling()
