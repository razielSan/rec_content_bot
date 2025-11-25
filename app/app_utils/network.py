from typing import Optional
import base64

from aiohttp import ClientSession

from core.response import LoggingData, ResponseData
from error_handlers.network import error_handler_for_the_website


async def get_and_save_image(
    data_requests: str,
    path_img: str,
    session: ClientSession,
    logging_data: LoggingData,
    base_64: Optional[bool] = None,
) -> ResponseData:
    """
    Сохраняет data_requests по указанному если base_64 = True.

    Если data_requests это URL.Заходит по url, скачивает изображение
    и сохраняет его по указанному пути

    Args:
        data_requests (str): url для скачивания или строка в кодировке base64
        path_img (str): Путь до картинки
        session (ClientSession): сессия для запроса
        logging_data (LoggingData): обьект класса LoggingData содержащий в себе логгер и имя роутера
        base_64 (Optional[bool], optional): Проверка на кодировку base_64. По умолачанию None

    Returns:
        ResponseData: Объект с результатом запроса.

        Атрибуты ResponseData:
            - message (Any | None): Данные успешного ответа (если запрос прошёл успешно).
            - error (str | None): Описание ошибки, если запрос завершился неудачей.
            - status (int): HTTP-код ответа. 0 — если ошибка возникла на клиентской стороне.
            - url (str): URL, по которому выполнялся запрос.
            - method (str): HTTP-метод, использованный при запросе.
    """
    if base_64:
        image_file = base64.b64decode(data_requests)
        with open(path_img, "wb") as image:
            image.write(image_file)
    else:
        # Делаем запрос на сайт для получения данных о картинке
        response: ResponseData = await error_handler_for_the_website(
            session=session,
            url=data_requests,
            logging_data=logging_data,
            data_type="BYTES",
            timeout=180,
            function_name=get_and_save_image.__name__,
        )

        if response.error:
            return response

        # Сохраняем картинку по переданному пути
        with open(path_img, "wb") as file:
            file.write(response.message)

    return ResponseData(
        message=path_img,
        url="<unknown>",
        method="GET",
        status=200,
    )
