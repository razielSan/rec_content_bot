from typing import Optional, Tuple, List, Callable
from pathlib import Path
from logging import (
    Formatter,
    StreamHandler,
    FileHandler,
    getLogger,
    Logger,
    ERROR,
    INFO,
    WARNING,
)
from sys import stdout

from core.response import LoggingData
from core.logging import LoggerStorage


def setup_bot_logging(
    bot_name: str,
    base_path: Path,
    log_format: str,
    date_format: str,
    router_name: Optional[str] = None,
    root_path: Optional[Path] = False,
) -> Tuple[Logger, Logger, Logger]:
    """
    Создаем логгеры для бота.

    Обычный, предупреждающий и для ошибок
    Логи будут лежать в logs/<bot_name>/<тип логгирования>.log

    Args:
        bot_name: (str): Имя бота
        base_path (Path): Путь до папки с логами
        log_format (str): формат записи в лог
        date_format (str): Временной формат записи в лог
        router_name (str, optional): Имя папки для конкретного роутера, если нужно,
        если нет будет сохранятся в base_path
        root_path (str, Optional):  По умолчанию(False) логгирует в папку по имени бота(
            True - логирует в глобальный лог
        )
    """
    # Формиурем имя для логгера
    logger_name: str = router_name if router_name else bot_name

    # Если root_path передан, пропускаем - логируем в глобальный лог
    # Если root_path по умолчанию(False) - логируем в папку по имени бота
    if not root_path:
        base_path: Path = base_path / bot_name  # Путь до папки с логами
    # Если перадано имя конкретного роутера и логгер не ялвяется глобальным
    if router_name and not root_path:
        base_path: Path = base_path / router_name
    info_path: Path = base_path / "info.log"
    warning_path: Path = base_path / "warning.log"
    error_path: Path = base_path / "error.log"
    # Создаем папку "logs" если ее нет
    base_path.mkdir(parents=True, exist_ok=True)

    # задаем форматы логов
    formaterr: Formatter = Formatter(
        fmt=log_format,
        datefmt=date_format,
    )

    # Потоковый обработчик для вывода в консоль
    stream_handler: StreamHandler = StreamHandler(stream=stdout)
    stream_handler.setFormatter(formaterr)

    # Файловые обработчики
    file_handler_info: FileHandler = FileHandler(
        filename=info_path,
        encoding="utf-8",
    )
    file_handler_info.setFormatter(formaterr)

    file_handler_warning: FileHandler = FileHandler(
        filename=warning_path, encoding="utf-8"
    )
    file_handler_warning.setFormatter(formaterr)

    file_handler_error: FileHandler = FileHandler(
        filename=error_path,
        encoding="utf-8",
    )
    file_handler_error.setFormatter(formaterr)
    # Логгер для информации
    info_logger: Logger = getLogger(f"{logger_name}_info")
    if not info_logger.handlers:
        info_logger.setLevel(level=INFO)
        info_logger.addHandler(file_handler_info)
        info_logger.addHandler(stream_handler)

    # Логгер для предупреждения
    warning_logger: Logger = getLogger(f"{logger_name}_warning")
    if not warning_logger.handlers:
        warning_logger.setLevel(level=WARNING)
        warning_logger.addHandler(file_handler_warning)
        warning_logger.addHandler(stream_handler)

    # Логгер для ошибок
    error_logger: Logger = getLogger(f"{logger_name}_error")
    if not error_logger.handlers:
        error_logger.setLevel(level=ERROR)
        error_logger.addHandler(file_handler_error)
        error_logger.addHandler(stream_handler)

    info_logger.info(f"Логгер {logger_name} создан")
    return info_logger, warning_logger, error_logger


def init_loggers(
    bot_name: str,
    setup_bot_logging: Callable,
    log_format: str,
    date_format: str,
    base_path: str,
    log_data: LoggerStorage,
    list_router_name: Optional[List[str]] = None,
) -> None:
    """Добавляет в хранилище логгеров переданые логи.

    Args:
        bot_name (str): имя бота
        list_router_name (List[str]): Список из имен роутеров
        setup_bot_logging (Callable): функция которая создает логгер
        log_format (str): формат записи в лог
        date_format (str): формат записи времения
        base_path (str): путь к папке с логами
        log_data (LoggerStorage): экземпляр класса хранилища для логов
    """
    if bot_name in log_data.BOT_ROUTER_NAME:
        pass
    else:
        info, warning, error = setup_bot_logging(
            bot_name=bot_name,
            base_path=base_path,
            log_format=log_format,
            date_format=date_format,
        )
        log_data.BOT_ROUTER_NAME[bot_name] = LoggingData(
            info_logger=info,
            warning_logger=warning,
            error_logger=error,
            router_name=bot_name,
        )

    if list_router_name:
        for router_name in list_router_name:
            if router_name in log_data.BOT_ROUTER_NAME:
                pass
            else:
                info, warning, error = setup_bot_logging(
                    bot_name=bot_name,
                    base_path=base_path,
                    router_name=router_name,
                    log_format=log_format,
                    date_format=date_format,
                )
                log_data.BOT_ROUTER_NAME[router_name] = LoggingData(
                    info_logger=info,
                    warning_logger=warning,
                    error_logger=error,
                    router_name=router_name,
                )


def get_loggers(
    router_name: str,
    logging_data: LoggerStorage,
) -> LoggingData:
    """
    Возвращает хранилище для логов конкретного роутера.

    Если нет возвращает ошибку KeyError

    Args:
        router_name (str): имя роутера
        logging_data (LoggerSettings): экземпляр класса хранилища для логов

    Raises:
        KeyError: Нет такого роутера

    Returns:
        LoggingData: хранилище для логов
    """
    if router_name in logging_data.BOT_ROUTER_NAME:
        return logging_data.BOT_ROUTER_NAME[router_name]
    raise KeyError(f"Нет такого роутера - {router_name}")