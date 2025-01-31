import os

from telegram import Update, constants
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext, Application, ContextTypes

from ollama import ChatResponse
from ollama import Client

from dotenv import load_dotenv

# Токен вашего бота
TOKEN = os.getenv("BOT_TOKEN", "TOKEN")
USER_IDs = list(str(os.getenv("USER_ID", "162507919")).split(","))

if TOKEN == "TOKEN":
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN", "TOKEN")
    USER_IDs = list(str(os.getenv("USER_ID", "162507919")).split(","))


async def start(update: Update, context: CallbackContext):
    print(f"Бот запущен и ставит лайки за сообщения! 👍")


async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Проверяем, что сообщение пришло из группы
    if update.effective_chat.type == 'group':
        try:
            # Пересылаем сообщение в личный чат пользователя
            for user_id in USER_IDs:
                await context.bot.forward_message(
                    chat_id=int(user_id),
                    from_chat_id=update.effective_chat.id,
                    message_id=update.message.message_id
                )
        except Exception as e:
            print(f"Ошибка пересылки: {e}")


async def send_to_user(context: ContextTypes.DEFAULT_TYPE, message_str: str) -> None:
    try:
        for user_id in USER_IDs:
            await context.bot.send_message(
                chat_id=int(user_id),  # Замените на реальный ID пользователя
                text=message_str
            )
    except Exception as e:
        print(f"Ошибка отправки: {e}")


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
        response: ChatResponse = client.chat(model='qwen2.5:14b', messages=[
            {
                'role': 'user',
                'content': f"Содержит ли сообщение информацию о технической ошибке, ответь да или нет: {message_text}",
            },
        ])
        print(f"Получили ответ: {response['message']['content']}")
        if 'ДА' in str(response['message']['content']).upper():
            # Вызываем функцию с реакцией
            await forward_message(update, context)
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
