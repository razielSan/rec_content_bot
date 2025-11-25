from core.messages import DefaultMessages
from core.main import AppSettings
from app_utils.logging import setup_bot_logging

# Настройки всего приложения
app_settings: AppSettings = AppSettings()

# Дефолтные сообщения пользователю
messages: DefaultMessages = DefaultMessages()

# логгеры приложения
root_info_logger, root_warning_logger, root_error_logger = setup_bot_logging(
    bot_name=app_settings.BOT_ROOT_NAME,
    base_path=app_settings.PATH_LOG_FOLDER,
    root_path=True,
    date_format=app_settings.DATE_FORMAT,
    log_format=app_settings.LOG_FORMAT,
)
