from typing import Callable, Dict, List
import asyncio
import traceback

import aiohttp

from core.response import ResponseData, LoggingData
from error_handlers.network import error_handler_for_the_website


async def get_list_albums_for_discogs(
    style: str,
    per_page: int,
    url: str,
    year: int,
    update_progress: Callable,
    discogs_setting,
    session: aiohttp.ClientSession,
    logging_data: LoggingData,
) -> ResponseData:

    """
    Возвращает список альбомов исполнителей по жанру для сайта discogs.com.

    Args:
        style (str): Стиль музыки для поиска
        per_page (int): количество альбомов для поиска
        url (str): URL для запроса
        year (int): год для поиска альбомов
        update_progress (Callable): функция для отслеживания прогресса
        discogs_setting (_type_): Pydantic model с данными по discogs
        session (aiohttp.ClientSession): сессия запроса
        logging_data (LoggingData): Класс содержащий в себе логер и имя роутера

    Returns:
        ResponseData: Объект с результатом запроса.

        Атрибуты ResponseData:
            - message (Any | None): Данные успешного ответа (если запрос прошёл успешно).
            - error (str | None): Описание ошибки, если запрос завершился неудачей.
            - status (int): HTTP-код ответа. 0 — если ошибка возникла на клиентской стороне.
            - url (str): URL, по которому выполнялся запрос.
            - method (str): HTTP-метод, использованный при запросе.
    """
    # формируем параметры для запроса
    params: Dict = {
        "key": discogs_setting.KEY,
        "secret": discogs_setting.SECRET,
        "style": style,
        "year": year,
        "format": "Album",
        "per_page": per_page,
        "page": 1,
        "sort": "year",
        "sort_order": "desc",
    }

    headers: Dict = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }

    # формируем запрос для получения списка артистов
    response_artists_list: ResponseData = await error_handler_for_the_website(
        session=session,
        url=url,
        logging_data=logging_data,
        function_name=get_list_albums_for_discogs.__name__,
        params=params,
        headers=headers,
    )

    if response_artists_list.error:
        return response_artists_list

    list_artists: List = []

    set_repeat: set = set() # для удаления повторов альбомов
    count: int = 0 # для отображения прогресса
    for result in response_artists_list.message["results"]:
        master_url: str = result["master_url"]
        try:
            if master_url:
                # Проверяет на состояние отмены запроса
                cancel = await update_progress()
                if not cancel:
                    return

                await asyncio.sleep(2.5)

                # делаем запрос на получение main_release_url
                response: ResponseData = await error_handler_for_the_website(
                    session=session,
                    url=master_url,
                    logging_data=logging_data,
                    function_name=get_list_albums_for_discogs.__name__,
                    timeout=100,
                    headers=headers,
                )
                # если слишком много запросов то пропускаем
                if response.status == 404:
                    continue
                if response.error:
                    return response
                main_release_url: str = response.message["main_release_url"]

                # Проверяет на состояние отмены запроса
                cancel = await update_progress()

                if not cancel:
                    return

                await asyncio.sleep(2.5)

                # Делаем запрос на получение информацию об альбоме артиста
                data_artist: ResponseData = await error_handler_for_the_website(
                    session=session,
                    url=main_release_url,
                    logging_data=logging_data,
                    function_name=get_list_albums_for_discogs.__name__,
                    timeout=100,
                    headers=headers,
                )
                if data_artist.status == 404:
                    continue
                if data_artist.error:
                    return data_artist

            else:
                # Проверяет на состояние отмены запроса
                cancel = await update_progress()
                if not cancel:
                    return
                await asyncio.sleep(2.5)
                # Делаем запрос на получение информацию об альбоме артиста
                data_artist: ResponseData = await error_handler_for_the_website(
                    session=session,
                    url=result["resource_url"],
                    logging_data=logging_data,
                    function_name=get_list_albums_for_discogs.__name__,
                    timeout=100,
                    headers=headers,
                )
                if data_artist.status == 404:
                    continue
                if data_artist.error:
                    return data_artist

            # Проверяет на состояние отмены запроса
            cancel = await update_progress()
            if not cancel:
                return
            # Получаем количество песен в альбоме
            tracklist: int = len(data_artist.message["tracklist"])

            img: str = data_artist.message["images"][0]["uri150"]
            music = discogs_setting.model_validate(
                {
                    "TITLE": data_artist.message["title"],
                    "ARTISTS_NAME": data_artist.message["artists"][0]["name"],
                    "ALBUM_URL": data_artist.message["uri"],
                    "FORMATS": ", ".join(
                        data_artist.message["formats"][0]["descriptions"]
                    ).strip(", "),
                    "RELEASED": data_artist.message["released"],
                    "COUNTRY": data_artist.message["country"],
                    "STYLES": ", ".join(data_artist.message["styles"]).strip(", "),
                    "TRACKLIST": tracklist,
                    "IMG": data_artist.message["images"][0]["uri150"],
                }
            )

            # Обновляем прогресс скачивания
            count += 1
            await update_progress(data_state=count)

            # Проверяем есть ли повторящющиеся альбомы
            len_set: int = len(set_repeat)
            set_repeat.add(img)
            if len_set == len(set_repeat):
                pass
            else:
                list_artists.append(music)
        except Exception as err:
            print(err)
    list_artists.sort(key=lambda x: x.dict()["RELEASED"]) # сортируем альбом по дате выхода
    return ResponseData(
        message=list_artists[::-1],
        url=url,
        method="GET",
        status=200,
    )


def get_descripions_for_albums(album: Dict) -> ResponseData:
    """
    Формирует информацию об альбоме исполнителя.

    Возвращает обьект класса ResponseData с информацией об альбоме исполнителя

    Args:
        album (Dict): словарь с данными об альбоме

    Returns:
        ResponseData: Объект с результатом запроса.

        Атрибуты ResponseData:
            - message (Any | None): Данные успешного ответа (если запрос прошёл успешно).
            - error (str | None): Описание ошибки, если запрос завершился неудачей.
            - status (int): HTTP-код ответа. 0 — если ошибка возникла на клиентской стороне.
            - url (str): URL, по которому выполнялся запрос.
            - method (str): HTTP-метод, использованный при запросе.
    """
    data: str = ""
    data += f'{album["ARTISTS_NAME"]}\n\n'
    data += f"Страна: {album['COUNTRY']}\n"
    data += f"Название альбома: {album['TITLE']}\n"
    data += f"Формат {album['FORMATS']}\n"
    data += f"Жанры: {album['STYLES']}\n"
    data += f"Дата выхода: {album['RELEASED']}\n\n"
    data += f"Количество песне в альбоме: {album['TRACKLIST']}\n\n"
    data += album["ALBUM_URL"]

    return ResponseData(message=data, url="<unknown>", status=0, method="<unknown>")
