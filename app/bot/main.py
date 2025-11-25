import aiohttp

from bot.extension import bot, dp, bot_settings, main_logger
from bot.views import main_router
from app_utils.filesistem import ensure_derictories

# создаем общие пути
ensure_derictories(
    bot_settings.PATH_BOT_STATIC_FOLDER, bot_settings.PATH_BOT_TEMP_FOLDER,
)


async def run_rec_content_bot():
    """Подлючает все параметры для бота и запускает его."""
    # Встаем в try/except чтобы отловить все что не попало в middleware
    try:
        await bot.set_my_commands(
            commands=bot_settings.LIST_BOT_COMMANDS  # Добавляет команды боту
        )  # Добавляет команды боту
        await bot.delete_webhook(
            drop_pending_updates=True
        )  # Игнорирует все присланные сообщение пока бот не работал

        dp.include_router(main_router)

        # Создаем глобальную сессию для всего бота. Будет доступ в роутерах через
        # название указанное ниже
        async with aiohttp.ClientSession() as session:
            dp["session"] = session

            main_logger.info_logger.info(msg=f"{bot_settings.BOT_NAME} запущен")

            await dp.start_polling(bot)

    except Exception as err:
        main_logger.error_logger.exception(
            f"Критическая ошибка при работа бота {bot_settings.BOT_NAME}: {err}"
        )
