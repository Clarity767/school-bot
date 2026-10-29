import os
import time
from threading import Thread
import telebot
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))

bot = telebot.TeleBot(TOKEN)

user_last_message_time = {}
SPAM_COOLDOWN = 3
BLOCKED_USERS = set()

app = Flask('')

@app.route('/')
def home():
    return "Бот працює 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 Привіт! Це анонімна онлайн-скринька скарг і пропозицій.\n\n"
        "💬 Напиши сюди будь-яку ідею, зауваження чи проблему. "
        "Твоє ім'я, юзернейм чи інші дані **не зберігаються і не передаються** — середовище повністю анонімне."
    )
    bot.send_message(message.chat.id, welcome_text)

@bot.message_handler(commands=['block'])
def block_user(message):
    if message.chat.id != ADMIN_ID:
        return
    
    parts = message.text.split()
    if len(parts) > 1 and parts[1].isdigit():
        blocked_id = int(parts[1])
        BLOCKED_USERS.add(blocked_id)
        bot.send_message(ADMIN_ID, f"🚫 Користувача `{blocked_id}` заблоковано.", parse_mode="Markdown")
    else:
        bot.send_message(ADMIN_ID, "⚠️ Використання: `/block <user_id>`", parse_mode="Markdown")

@bot.message_handler(commands=['unblock'])
def unblock_user(message):
    if message.chat.id != ADMIN_ID:
        return
    
    parts = message.text.split()
    if len(parts) > 1 and parts[1].isdigit():
        unblocked_id = int(parts[1])
        BLOCKED_USERS.discard(unblocked_id)
        bot.send_message(ADMIN_ID, f"✅ Користувача `{unblocked_id}` розблоковано.", parse_mode="Markdown")
    else:
        bot.send_message(ADMIN_ID, "⚠️ Використання: `/unblock <user_id>`", parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_anonymous_messages(message):
    user_id = message.chat.id

    if user_id == ADMIN_ID:
        bot.send_message(
            ADMIN_ID, 
            "⚠️ Ти — адміністратор цього бота. Щоб відповісти комусь, скористайся іншим способом або пиши напряму."
        )
        return

    if user_id in BLOCKED_USERS:
        bot.send_message(user_id, "❌ Ви заблоковані адміністратором цього бота.")
        return

    current_time = time.time()
    if user_id in user_last_message_time:
        if current_time - user_last_message_time[user_id] < SPAM_COOLDOWN:
            bot.send_message(
                user_id, 
                "⏳ Зачекайте кілька секунд перед надсиланням наступного повідомлення."
            )
            return
    user_last_message_time[user_id] = current_time

    if message.text:
        if len(message.text) > 1000:
            bot.send_message(
                user_id, 
                "⚠️ Повідомлення занадто довге! Максимальна довжина — 1000 символів."
            )
            return

        admin_message = (
            f"📥 **Нове анонімне повідомлення:**\n\n"
            f"{message.text}\n\n"
            f"🆔 `ID відправника:` `{user_id}`\n"
            f"⚙️ `Заблокувати:` `/block {user_id}`"
        )
        
        bot.send_message(ADMIN_ID, admin_message, parse_mode="Markdown")
        bot.send_message(user_id, "✅ Твоє повідомлення успішно та анонімно надіслано адміністратору!")
    else:
        bot.send_message(
            user_id, 
            "⚠️ Будь ласка, надсилай своє повідомлення **текстом**. Медіафайли блокуються в цілях безпеки."
        )

if __name__ == '__main__':
    keep_alive()
    print("Бот запущено і захищено...")
    bot.infinity_polling()