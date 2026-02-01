import logging
import os
from telegram import Update
from telegram.ext import Application, ChatJoinRequestHandler, ContextTypes

# Логи
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен из переменных окружения
TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    logger.error("BOT_TOKEN не найден!")
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

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
        logger.info(f"Заявка одобрена для пользователя {request.from_user.id}")
    except Exception as e:
        logger.error(f"Ошибка одобрения заявки: {e}")
        return

    # Отправляем приветствие в личку
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

    # Добавляем обработчик заявок на вступление
    application.add_handler(ChatJoinRequestHandler(handle_join_request))

    # Настройки webhook для Render
    PORT = int(os.environ.get("PORT", "8443"))
    HOST = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

    if not HOST:
        logger.error("RENDER_EXTERNAL_HOSTNAME не найден!")
        raise ValueError("RENDER_EXTERNAL_HOSTNAME не найден")

    webhook_path = f"/{TOKEN}"
    webhook_url = f"https://{HOST}{webhook_path}"

    logger.info(f"Установка webhook на: {webhook_url}")

    # Устанавливаем webhook
    await application.bot.set_webhook(
        url=webhook_url,
        allowed_updates=Update.ALL_TYPES
    )

    # Запускаем приложение (это включает сервер webhook)
    await application.initialize()
    await application.start()
    await application.updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=webhook_path,
        webhook_url=webhook_url
    )

    # Держим процесс живым
    import asyncio
    await asyncio.Event().wait()  # бесконечное ожидание

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())