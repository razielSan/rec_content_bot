from aiogram import Bot, Dispatcher

from bot.config.bot_settings import BotSettings
from app_utils.logging import init_loggers, setup_bot_logging, get_loggers
from settings.response import app_settings
from core.logging import LoggerStorage
from bot.config.models.main import BaseGeneration
from app_utils.keyboards import get_total_buttons_reply_kb


# Получаем доступ ко всем моделям
models_settings: BaseGeneration = BaseGeneration()


# Создаем клавиатуру для главного меню
get_button_start_bot_menu = get_total_buttons_reply_kb(
    list_text=[
        models_settings.music_models.START_BOT_MENU_REPLY_TEXT,
        models_settings.video_models.START_BOT_MENU_REPLY_TEXT,
    ],
    quantity_button=1,
)


# Создаем хранилище логгеров
logging_data = LoggerStorage()

# Получаем настройки бота
bot_settings = BotSettings()

# Создаем бота и диспетчер
bot: Bot = Bot(token=bot_settings.TOKEN)
dp: Dispatcher = Dispatcher()


# Инициализируем логи
init_loggers(
    bot_name=bot_settings.BOT_NAME,
    setup_bot_logging=setup_bot_logging,
    log_format=app_settings.LOG_FORMAT,
    date_format=app_settings.DATE_FORMAT,
    base_path=app_settings.PATH_LOG_FOLDER,
    log_data=logging_data,
    list_router_name=[
        models_settings.music_models.SERVICE_ID,
        models_settings.video_models.SERVICE_ID,
    ],
)

# Получаем логгеры
main_logger = get_loggers(
    router_name=bot_settings.BOT_NAME,
    logging_data=logging_data,
)

music_logger = get_loggers(
    router_name=models_settings.music_models.SERVICE_ID,
    logging_data=logging_data,
)

video_logger = get_loggers(
    router_name=models_settings.video_models.SERVICE_ID,
    logging_data=logging_data,
)
