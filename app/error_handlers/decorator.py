from typing import Optional, Callable
import functools
from asyncio import exceptions

from error_handlers.format import format_errors_message
from core.response import LoggingData, ResponseData
from settings.response import messages


def safe_async_execution(logging_data: Optional[LoggingData] = None):
    """
    Декоратор оборчивающий асинхронную функцию в try/except для перхвата всех возможных ошибок.

    При ошибке в ходе выполнения функции выкидывает обьект класса ResponseData

    Args:
        logger_data (Optional[LoggingData], optional): Класс содержащий логгер и имя роутера.По умолчанию None
    """

    def decorator(function: Callable):
        @functools.wraps(function)
        async def wrapper(*args, **kwargs):
            try:
                return await function(*args, **kwargs)

            except exceptions.CancelledError:
                print("Остановка работы процесса пользователем")
                return ResponseData(
                    message="Остановка работы процесса пользователем",
                    status=0,
                    method="<unknown>",
                    url="<unknown>",
                )

            except Exception as err:
                if logging_data:
                    logging_data.error_logger.exception(
                        format_errors_message(
                            name_router=logging_data.router_name,
                            method="<unknown>",
                            status=0,
                            url="<unknown>",
                            error_text=err,
                            function_name=function.__name__,
                        )
                    )
                else:
                    print(err)
                return ResponseData(
                    error=messages.SERVER_ERROR,
                    status=0,
                    method="<unknown>",
                    url="<unknown>",
                )

        return wrapper

    return decorator


def safe_sync_execution(logging_data: Optional[LoggingData] = None):
    """
        Декоратор оборчивающий синхронную функцию в try/except для перхвата всех возможных ошибок
        При ошибке в ходе выполнения функции выкидвает обьект класса ResponseData

    Args:
        logger_data (Optional[LoggingData], optional): Класс содержащий логгер и имя роутера.По умолчанию None
    """

    def decorator(function: Callable):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as err:
                if logging_data:
                    logging_data.error_logger.exception(
                        format_errors_message(
                            name_router=logging_data.router_name,
                            method="<unknown>",
                            status=0,
                            url="<unknown>",
                            error_text=err,
                            function_name=function.__name__,
                        )
                    )
                else:
                    print(err)
                return ResponseData(
                    error=messages.SERVER_ERROR,
                    status=0,
                    method="<unknown>",
                    url="<unknown>",
                )

        return wrapper

    return decorator
