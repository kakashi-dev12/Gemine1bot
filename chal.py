import telebot
import requests
import json

# 🔑 Replace with your real keys
BOT_TOKEN = "7813983435:AAFzD6Eci1MDcdgbtKUf25hXH9Ic-VoNJUo"
GEMINI_API_KEY = "AIzaSyAUrOC5jNTOxjU0a1OUE1lWP4_TanxTi-A"

bot = telebot.TeleBot(BOT_TOKEN)

# 💾 Memory file for storing chats
MEMORY_FILE = "memory.json"

# 🧠 Load memory
def load_memory():
    try:
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

# 💾 Save memory
def save_memory(memory):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f)
# 🌟 Part 2 — improved: shows real error + uses up-to-date endpoint
def ask_gemini(user_input, user_id):
    memory = load_memory()
    history = memory.get(str(user_id), [])
    # ✅ correct structure: each turn is a dict with "parts":[{"text":...}]
    history.append({"role": "user", "parts": [{"text": user_input}]})

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-2.0-flash:generateContent"      # 👈 gemini-pro is retired
        f"?key={GEMINI_API_KEY}"
    )
    payload = {
        "contents": history,
        "generationConfig": {
            "temperature": 0.85,
            "topK": 1,
            "topP": 1,
            "maxOutputTokens": 150
        }
    }

    res = requests.post(url, json=payload, timeout=30)

    if res.ok:
        reply = res.json()["candidates"][0]["content"]["parts"][0]["text"]
        history.append({"role": "model", "parts": [{"text": reply}]})
        memory[str(user_id)] = history[-10:]          # keep last 10 turns
        save_memory(memory)
        return reply
    else:
        # 👀 send the exact error back so you can see what’s wrong
        err = res.json().get("error", {}).get("message", "Unknown error")
        return f"😕 API error {res.status_code}: {err}"
# 🌸 Start command
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "Hii bestiee! 🤍 I'm your virtual dost. Bata kya chal raha hai?")

# 💬 Chat handling
@bot.message_handler(func=lambda m: True)
def chat(message):
    user_input = message.text
    bot.send_chat_action(message.chat.id, 'typing')
    response = ask_gemini(user_input, message.from_user.id)
    bot.reply_to(message, response)

# 🔄 Start polling
bot.remove_webhook()
bot.polling()
