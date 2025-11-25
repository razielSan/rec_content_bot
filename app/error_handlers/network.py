from typing import Dict
import asyncio

import aiohttp

from error_handlers.format import format_errors_message
from core.response import ResponseData, LoggingData
from settings.response import messages


async def safe_read_response(resp):
    """Проверяет в каком формате был передан ответ с сайта и возвращает текст ответа.

    Args:
        resp (_type_): запрос для сайта

    Returns:
        _type_: Возвращает содержание текста ответа с сайта
    """
    try:
        content_type = resp.headers.get("Content-Type", "").lower()
        if "application/json" in content_type:
            data = await resp.json()
            return data
        return await resp.text()
    except Exception:
        return "<no body>"


async def error_handler_for_the_website(
    session: aiohttp.ClientSession,
    url: str,
    logging_data: LoggingData,
    data_type="JSON",
    timeout=15,
    method="GET",
    data=None,
    headers=None,
    function_name=None,
    json=None,
    params=None,
) -> ResponseData:
    """
    Асинхронный запрос с обработками ошибок для сайтов.

    Args:
        session (_type_): асинхронная сессия запроса
        url (str): URL сайта
        logging_data: (LoggingData): Класс содержащий логгер и имя роутера для логгирования
        data_type (str, optional): Тип возвращаемых данных.По умолчанию JSON('JSON', 'TEXT', 'BYTES')
        timeout (int, optional): таймаут запроса в секундах
        method (str, optional): Метод запроса. 'POST' или "GET"
        data (_type_, optional): Данные для POST запроса
        headers (dict): Заголовки запроса
        function_name (str): Имя функции в которой произошла ошибка

    Returns:
        ResponseData: Объект с результатом запроса.

        Атрибуты ResponseData:
            - message (Any | None): Данные успешного ответа (если запрос прошёл успешно).
            - error (str | None): Описание ошибки, если запрос завершился неудачей.
            - status (int): HTTP-код ответа. 0 — если ошибка возникла на клиентской стороне.
            - url (str): URL, по которому выполнялся запрос.
            - method (str): HTTP-метод, использованный при запросе.
    """
    timeout_cfg: aiohttp.ClientTimeout = aiohttp.ClientTimeout(total=timeout)
    try:
        async with session.request(
            method=method,
            url=url,
            timeout=timeout_cfg,
            data=data,
            headers=headers,
            json=json,
            allow_redirects=True,
            params=params,
        ) as resp:
            # Для удобного логгирования
            if resp.status in [403, 404, 429]:

                # Тело ответа запроса
                error_body = await safe_read_response(resp=resp)

                # Формируем дефолтные сообщения
                default_messages: Dict = {
                    403: "Доступ к сайту запрещен",
                    404: "Cервер не может найти запрошенный ресурс",
                    429: "Слишком много запросов к серверу",
                }

                # Формируем ответ для пользователя
                error_message_str: str = (
                    error_body.get("message", default_messages[resp.status])
                    if isinstance(error_body, dict)
                    else default_messages[resp.status]
                )

                logg_error_str: str = str(error_body)[:500]

                logging_data.error_logger.error(
                    msg=format_errors_message(
                        name_router=logging_data.router_name,
                        method=resp.method,
                        status=resp.status,
                        url=url,
                        error_text=logg_error_str,
                        function_name=function_name,
                    )
                )

                return ResponseData(
                    status=resp.status,
                    error=error_message_str,
                    url=url,
                    method=resp.method,
                )

            elif resp.status != 200 and resp.status != 202:
                error_body = await safe_read_response(resp=resp)

                logg_error_str: str = str(error_body)[:500]

                logging_data.error_logger.error(
                    msg=format_errors_message(
                        name_router=logging_data.router_name,
                        method=resp.method,
                        status=resp.status,
                        url=url,
                        error_text=logg_error_str,
                        function_name=function_name,
                    )
                )

                return ResponseData(
                    status=resp.status,
                    error=messages.UNKNOWN_STATUS_ERROR,
                    url=url,
                    method=resp.method,
                )
            if data_type.upper() == "JSON":
                message_body = await resp.json()
                return ResponseData(
                    message=message_body,
                    status=resp.status,
                    url=url,
                    method=resp.method,
                )
            elif data_type.upper() == "TEXT":
                message_body: str = await resp.text()
                return ResponseData(
                    message=message_body,
                    status=resp.status,
                    url=url,
                    method=resp.method,
                )
            else:
                message_body: bytes = await resp.read()
                return ResponseData(
                    message=message_body,
                    status=resp.status,
                    url=url,
                    method=resp.method,
                )
    except aiohttp.ClientError as err:
        error_message: str = f"Ошибка сети при запросе:\n{err}"

        logging_data.error_logger.exception(
            msg=format_errors_message(
                name_router=logging_data.router_name,
                method=method,
                status=0,
                url=url,
                error_text=error_message,
                function_name=function_name,
            )
        )

        return ResponseData(
            error=messages.NETWORK_ERROR,
            status=0,
            url=url,
            method=method,
        )
    except asyncio.TimeoutError as err:
        error_message: str = f"Ожидание от сервера истекло:\n{err}"

        logging_data.error_logger.exception(
            msg=format_errors_message(
                name_router=logging_data.router_name,
                method=method,
                status=0,
                url=url,
                error_text=error_message,
                function_name=function_name,
            )
        )

        return ResponseData(
            error=messages.TIMEOUT_ERROR,
            status=0,
            url=url,
            method=method,
        )
    except Exception as err:
        error_message: str = f"Неизвестная ошибка при запросе:\n{err}"

        logging_data.error_logger.exception(
            msg=format_errors_message(
                name_router=logging_data.router_name,
                method=method,
                status=0,
                url=url,
                error_text=error_message,
                function_name=function_name,
            )
        )

        return ResponseData(
            error=messages.SERVER_ERROR,
            status=0,
            url=url,
            method=method,
        )
