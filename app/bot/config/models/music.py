from typing import Optional

from pydantic import BaseModel


class Discogs(BaseModel):
    """Модель для сайта https://www.discogs.com/"""

    SERVICE_NAME: str = "Discogs"
    SERVICE_ID: str = "discogs"

    # Словарь со стилями и их названиями для кнопок
    DICT_STYLES: dict = {
        "Punk": "1⃣ Punk",
        "Hardcore": "2⃣ Hardcore",
        "Crust": "3⃣ Crust",
        "Grindcore": "4⃣ Grindcore",
        "Post-Punk": "5⃣ Post-Punk",
        "Heavy Metal": "6⃣ Heavy Metal",
        "Thrash": "7⃣ Thrash",
        "Crossover thrash": "8⃣ Crossover thrash",
        "Black Metal": "9⃣ Black Metal",
        "Death Metal": "1⃣0⃣ Death Metal",
    }

    # URL для сайта
    URL_SEARCH: str = "https://api.discogs.com/database/search"

    # Уникальные данные для сайта
    KEY: Optional[str] = None
    SECRET: Optional[str] = None

    # Данные для парсинга
    TITLE: Optional[str] = None
    ARTISTS_NAME: Optional[str] = None
    ALBUM_URL: Optional[str] = None
    FORMATS: Optional[str] = None
    RELEASED: Optional[str] = None
    COUNTRY: Optional[str] = None
    STYLES: Optional[str] = None
    TRACKLIST: Optional[int] = None
    IMG: Optional[str] = None
    COUNT_ALBUMS_SEARCH: int = 50


class NewMusicItemsModels(BaseModel):
    """Модель содержащая другие модели по поиску музыкальных новинок."""

    SERVICE_NAME: str = "New_Music"
    SERVICE_ID: str = "new_music"

    # Данные кнопок для подлкючаемых моделей
    CALLBACK_BUTTON_TEXT_DISCOGS: str = "1⃣ discogs"
    CALLBACK_BUTTON_DATA_DISCOGS: str = "new_music discogs"

    discogs: Discogs = Discogs()


class MusicModels(BaseModel):
    """Общий класс для генерации музакальных моделей."""

    SERVICE_NAME: str = "Music"
    SERVICE_ID: str = "music"

    # Данные кнопок для подлключаемых моделей
    CALLBACK_BUTTON_TEXT_NEW_MUSIC: str = "🎻 Музыкальные новинки"
    CALLBACK_BUTTON_DATA_NEW_MUSIC: str = "music new_music"
    START_BOT_MENU_REPLY_TEXT: str = "🎧 Mузыка"

    new_music: NewMusicItemsModels = NewMusicItemsModels()
