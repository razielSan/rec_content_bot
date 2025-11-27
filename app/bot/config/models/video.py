from typing import Optional, Dict
from pathlib import Path

from pydantic import BaseModel


class Kinopoisk(BaseModel):
    """Модель рекомендательной системы для кинопоиска."""

    SERVICE_NAME: str = "Kinopoisk"
    SERVICE_ID: str = "kinopoisk"

    API_KEY: Optional[str] = None

    # URL для запросов
    URL_SEARCH_VIDEO_NAME: str = (
        "https://api.kinopoisk.dev/v1.4/movie/search?page=1&limit={limit}&query={name}"
    )
    URL_SEARCH_UNIVERSAL_VIDEO: str = (
        "https://api.kinopoisk.dev/v1.4/movie?page=1&limit={limit}"
    )

    PATH_TO_FOLDER_DEFOLT_IMAGE_KINOPOISK: Path = (
        Path(__file__).resolve().parent.parent.parent
        / "static"
        / "img"
        / "video"
        / "viewing_advice"
        / "kinopoisk"
    )
    PATH_TO_FILENAME_DEFOLTE_IMAGE_KINOPOISK: Path = (
        PATH_TO_FOLDER_DEFOLT_IMAGE_KINOPOISK / "none.png"
    )

    HEADERS: Dict = {
        "accept": "application/json",
        "X-API-KEY": None,
    }


class ViewingAdvieModels(BaseModel):
    """Общий класс для моделей для рекомендаций по названию фильма."""

    SERVICE_NAME: str = "ViewingAdvie"
    SERVICE_ID: str = "viewing_advice"

    # Данные кнопок для подключаемых моделей
    CALLBACK_BUTTON_TEXT_KINOPOISK: str = "1⃣ Kinopoisk"
    CALLBACK_BUTTON_DATA_KINOPOISK: str = "viewing_advice kinopoisk"

    kinopoisk: Kinopoisk = Kinopoisk()


class VideoModels(BaseModel):
    """Общий класс для генерации видео моделей."""

    SERVICE_NAME: str = "Video"
    SERVICE_ID: str = "video"

    # Данные кнопок для подключаемых моделей
    CALLBACK_BUTTON_TEXT_VIEWING_ADVICE: str = "📚 Совет По Названию Фильма"
    CALLBACK_BUTTON_DATA_VIEWING_ADVICE: str = "video viewing_advice"
    START_BOT_MENU_REPLY_TEXT: str = "🎦 Видео"

    viewing_advice: ViewingAdvieModels = ViewingAdvieModels()
