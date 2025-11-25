import asyncio
import signal
import sys


from bot.main import run_rec_content_bot
from bot.extension import bot
from settings.response import root_warning_logger, root_info_logger

# Меняет тип event_loop для виндоус чтобы при нажатии ctl+c не было ошибки KeyboardInterrupt
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main() -> None:
    """Запуск основного приложения."""
    # Если платформа ни виндоус
    if sys.platform != "win32":
        # корректно завершает работу на сервере
        loop = asyncio.get_event_loop()
        stop_event = asyncio.Event()

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, stop_event.set)

        root_info_logger.info("Приложение запущен(Unix mode)")
        await asyncio.gather(run_rec_content_bot(), stop_event.wait())
    else:
        try:
            # Запускам бота
            root_info_logger.info("Приложение запущено (Windows mode)")
            await run_rec_content_bot()
        except Exception:
            pass
        finally:
            # Завершаем работy для windows
            root_info_logger.info("Приложение завершает работу")
            try:
                if getattr(bot, "session", None):
                    await bot.session.close()  # аккуратно закрываем сессию
            except RuntimeError:
                root_warning_logger.warning(
                    "Сессия уже была закрыта или event loop завершен"
                )
            except Exception as err:
                root_warning_logger.warning(f"Ошибка при закрытии сессии: {err}")
            root_info_logger.info("Приложение завершило работу корректно")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:  # Проглатываем ошибку KeyboardInterrupt для windows чтобы не отображалась
        root_warning_logger.warning("Приложение остановлено вручную (Ctrl+C)")
