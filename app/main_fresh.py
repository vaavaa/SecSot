import os

from telegram import Update, constants
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext, Application

from ollama import ChatResponse
from ollama import Client

from dotenv import load_dotenv

# Токен вашего бота
TOKEN = os.getenv("BOT_TOKEN", "TOKEN")

if TOKEN=="TOKEN":
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN", "TOKEN")

async def start(update: Update, context: CallbackContext):
     print(f"Бот запущен и ставит лайки за сообщения! 👍")


async def react_with_like(update: Update, context: CallbackContext):
    message = update.message
    chat_id = message.chat_id
    message_id = message.message_id

    try:
        # Ставим реакцию "лайк" (👍)
        await context.bot.set_message_reaction(
            chat_id=chat_id,
            message_id=message_id,
            reaction=[constants.ReactionEmoji.EYES],
            is_big=False  # Можно изменить на True для увеличенной анимации
        )
    except Exception as e:
        print(f"Ошибка при установке реакции: {e}")


async def analyze_message(update: Update, context: CallbackContext):

    message_text = update.message.text or "Медиа-контент"

    if not message_text:
        return
    client = Client(
        host='http://192.168.68.120:11434',
    )
    # Инициализация клиента Ollama
    try:
        response: ChatResponse = client.chat(model='llama3.1:latest', messages=[
            {
                'role': 'user',
                'content': f"Содержит ли сообщение информацию о технической ошибке, ответь да или нет: {message_text}",
            },
        ])
        print(f"Получили ответ: {response['message']['content']}")
        if 'ДА' in str(response['message']['content']).upper():
            # Вызываем функцию с реакцией
            await react_with_like(update, context)

    except Exception as e:
        print(f"Возникла ошибка с сообщением: {message_text} -- ошибка: {str(e)}")
    print(f"Проанализировано сообщение: {message_text}")


def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL, analyze_message))

    application.run_polling()


if __name__ == "__main__":
    print("Bot alive")
    main()