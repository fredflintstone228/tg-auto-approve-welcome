import logging
import os
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    ChatJoinRequestHandler,
    ContextTypes,
)

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен из переменных окружения (на Render)
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")

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
        logger.info(f"Одобрена заявка пользователя {request.from_user.id}")
    except Exception as e:
        logger.error(f"Ошибка одобрения: {e}")
        return

    # Отправляем приветствие в личные сообщения
    try:
        await context.bot.send_message(
            chat_id=request.from_user.id,
            text=WELCOME_TEXT
        )
        logger.info(f"Приветствие отправлено {request.from_user.id}")
    except Exception as e:
        logger.error(f"Ошибка отправки приветствия: {e}")

async def main():
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчик
    application.add_handler(ChatJoinRequestHandler(handle_join_request))

    # Настройки webhook
    PORT = int(os.environ.get("PORT", 8443))
    HOST = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

    if not HOST:
        raise ValueError("RENDER_EXTERNAL_HOSTNAME не найден!")

    webhook_path = f"/bot{TOKEN}"  # путь, чтобы было уникально
    webhook_url = f"https://{HOST}{webhook_path}"

    logger.info(f"Устанавливаем webhook → {webhook_url}")

    # Устанавливаем webhook
    await application.bot.set_webhook(
        url=webhook_url,
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True  # полезно при перезапуске
    )

    # Запускаем приложение в режиме webhook
    await application.initialize()
    await application.start()
    await application.updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=webhook_path,
        webhook_url=webhook_url
    )

    # Держим процесс живым
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())