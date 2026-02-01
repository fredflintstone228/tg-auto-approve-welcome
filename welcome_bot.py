import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, ContextTypes

# Логи для отладки
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен берём из переменной окружения
TOKEN = os.environ.get("BOT_TOKEN")

# Приветственное сообщение
WELCOME_TEXT = """
👋 Hallo! Schön, dass du da bist.

Dein erster Schritt zu echtem Online-Gewinn wartet: bis zu 700 € 💸 mit der ersten Kombination.

📩 Schreib mir direkt im Privat-Chat - @andreeas_keller, um alle Details zu bekommen!
"""


async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    request = update.chat_join_request

    # Одобряем заявку
    try:
        await context.bot.approve_chat_join_request(
            chat_id=request.chat.id,
            user_id=request.from_user.id
        )
        logger.info(f"Заявка одобрена для {request.from_user.id}")
    except Exception as e:
        logger.error(f"Ошибка одобрения: {e}")
        return

    # Отправляем приветствие в личные сообщения
    try:
        await context.bot.send_message(
            chat_id=request.from_user.id,
            text=WELCOME_TEXT,
            parse_mode=None  # можно оставить без parse_mode, если не нужны жирные/курсив
        )
        logger.info(f"Приветствие отправлено {request.from_user.id}")
    except Exception as e:
        logger.error(f"Не удалось отправить приветствие {request.from_user.id}: {e}")


def main():
    if not TOKEN:
        logger.error("BOT_TOKEN не найден в переменных окружения!")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчик заявок на вступление
    application.add_handler(ChatJoinRequestHandler(handle_join_request))

    # Webhook настройки для Render
    PORT = int(os.environ.get("PORT", 8443))
    HOST = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "localhost")

    webhook_url = f"https://{HOST}/{TOKEN}"

    logger.info(f"Устанавливаем webhook на: {webhook_url}")

    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=webhook_url,
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()