from typing import List, Dict
import random
import aiohttp


from error_handlers.network import error_handler_for_the_website
from core.response import LoggingData, ResponseData


async def get_recommender_video_for_kinopoisk(
    session: aiohttp.ClientSession,
    url_search_universal_video: str,
    list_genres: List,
    limit: int,
    type_video: str,
    rating: str,
    headers: Dict,
    logging_data: LoggingData,
    timeout: int,
) -> ResponseData:
    aiohttp.ClientSession
    """
    Возвращает рекомендованные фильмы из сайта  https://www.kinopoisk.ru/.

    Args:
        session (aiohttp.ClientSession): Сессия для запроса
        url_search_universal_video (str): URL для запроса
        list_genres (List): Список жанров фильма
        limit (int): Количество выдаваемых фильмов
        type_video (str): Тип видео
        rating (str): Рейтинг видео
        headers (Dict): Заголовки для запроса
        logging_data (LoggingData): Обьект класса LoggingData сорежащий логгер и имя роутера

    Returns:
        ResponseData: Объект с результатом запроса.

        Атрибуты ResponseData:
            - message (List | None): Данные успешного ответа (если запрос прошёл успешно).
              Cодержит список из словарей рекомендованных фильмов для кинопоиска    
            - error (str | None): Описание ошибки, если запрос завершился неудачей.
            - status (int): HTTP-код ответа. 0 — если ошибка возникла на клиентской стороне.
            - url (str): URL, по которому выполнялся запрос.
            - method (str): HTTP-метод, использованный при запросе
    """
    # Создает случайный список из двух жанров в которых снят фильм
    array_genres: List = []
    for genre in list_genres:
        array_genres.append(genre.get("name"))
    if len(array_genres) > 1:
        array_genres = random.sample(array_genres, 2)

    for genre in array_genres:
        url_search_universal_video: str = (
            url_search_universal_video + f"&genres.name={genre}"
        )
        # url = url + f"&genres.name={genre}"

    url_search_universal_video += f"&type={type_video}"
    url_search_universal_video += f"&rating.kp={rating}"

    array_recommender: ResponseData = await error_handler_for_the_website(
        session=session,
        url=url_search_universal_video,
        headers=headers,
        timeout=timeout,
        logging_data=logging_data,
        function_name=get_recommender_video_for_kinopoisk.__name__,
    )
    if array_recommender.error:
        return array_recommender

    array_recommender = array_recommender.message.get("docs")
    random.shuffle(array_recommender)

    return ResponseData(
        message=array_recommender[:limit],
        url=url_search_universal_video,
        method="GET",
        status=200,
    )


def get_description_video_from_kinopoisk(data: Dict) -> ResponseData:
    """
    Возвращает описание фильма для кинопоиска.

    Args:
        data (Dict): Словарь содержащий данные о фильме

    Returns:
        ResponseData: Объект с результатом запроса.

        Атрибуты ResponseData:
            - message (Any | None): Данные успешного ответа (если запрос прошёл успешно).
              Содержит строку с описанием фильма 
            - error (str | None): Описание ошибки, если запрос завершился неудачей.
            - status (int): HTTP-код ответа. 0 — если ошибка возникла на клиентской стороне.
            - url (str): URL, по которому выполнялся запрос.
            - method (str): HTTP-метод, использованный при запросе
    """
    name: str = f'{data.get("name")}\n\n'

    array_genres: List = []
    if data.get("genres", 0):
        for genre in data.get("genres"):
            array_genres.append(genre.get("name"))
    array_countries: List = []
    if data.get("countries", 0):
        for country in data.get("countries"):
            array_countries.append(country.get("name"))
    if data.get("alternativeName", 0):
        name += f"Другое название: {data.get('alternativeName')}\n"
    if data.get("type", 0):
        name += f"Тип видео: {data.get('type')}\n"
    if data.get("year", 0):
        name += f"Год выхода: {data.get('year')}\n"
    if data.get("description", 0):
        descripton: str = f"{data['description'][:200]}...."
        name += f"Описание: {descripton}\n"
    if data.get("shortDescription", 0):
        name += f"Короткое описание: {data['shortDescription']}\n"
    if data.get("movieLength", 0):
        name += f"Длина фильма: {data['movieLength']} м.\n"
    if data["rating"].get("kp", 0):
        data_kp = data["rating"].get("kp")
        name += f"Рейтинг на кинпоиске: {data_kp}\n"
    if data["rating"].get("imdb", 0):
        data_imdb = data["rating"].get("imdb")
        name += f"Рейтинг на imdb: {data_imdb}\n"

    genres = ""
    if array_genres:
        genres: str = "Список жанров: "
        for g in array_genres:
            genres += f"{g},"
        genres = genres.strip(",")
    if genres:
        name += f"{genres}\n"

    countries = ""
    if array_countries:
        countries: str = "Страны: "
        for c in array_countries:
            countries += f"{c},"
        countries = countries.strip(",")
    if countries:
        name += f"{countries}\n"

    return ResponseData(
        message=name,
        status=9,
        method="<unknown>",
        url="<unknown>",
    )
