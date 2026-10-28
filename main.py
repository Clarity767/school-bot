import telebot
from dotenv import load_dotenv
import os

load_dotenv()


TOKEN = os.getenv('BOT_TOKEN')

ADMIN_ID = int(os.getenv('ADMIN_ID'))

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 Привіт! Це анонімна онлайн-скринька скарг і пропозицій.\n\n"
        "💬 Напиши сюди будь-яку ідею, зауваження чи проблему. "
        "Твоє ім'я, юзернейм чи інші дані **не зберігаються і не передаються** —середовище повністю анонімне."
    )
    bot.send_message(message.chat.id, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_anonymous_messages(message):

    if message.chat.id == ADMIN_ID:
        bot.send_message(
            ADMIN_ID, 
            "⚠️ Ти — адміністратор цього бота. Щоб відповісти комусь, скористайся іншим способом або пиши напряму."
        )
        return

    if message.text:

        admin_message = f"📥 **Нове анонімне повідомлення:**\n\n{message.text}"

        bot.send_message(ADMIN_ID, admin_message, parse_mode="Markdown")
        

        bot.send_message(message.chat.id, "✅ Твоє повідомлення успішно та анонімно надіслано адміністратору!")

        bot.send_message(
            message.chat.id, 
            "⚠️ Будь ласка, надсилай своє повідомлення **текстом**. Медіафайли не приймаються в цілях безпеки."
        )


if __name__ == '__main__':
    print("Бот запущено і готовий до роботи...")
    bot.infinity_polling()