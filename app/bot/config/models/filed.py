from pathlib import Path
from pydantic import BaseModel


class FieldGeneration(BaseModel):
    """Модель содежащая общие настройки для всех моделей."""

    # Основные параметры - обязательны к заполнению
    SERVICE_NAME: str = ""  # имя для роутера
    SERVICE_ID: str = ""  # параметр нужный для определеия путей, кнопок

    BOT_DIR: Path = Path(__file__).resolve().parent.parent.parent

    # Данные кнопок - обязательны к заполнению
    TEXT_PREFIX: str = ""
    TEXT_DATA: str = ""
    CALLBACK_PREFIX: str = ""
    CALLBACK_DATA: str = ""

    # Текст каллбэк кнопки
    @property
    def CALLBACK_BUTTON_TEXT(self):
        return f"{self.TEXT_PREFIX} {self.TEXT_DATA}"

    # Данные каллбэк кнопки
    @property
    def CALLBACK_BUTTON_DATA(self):
        return f"{self.CALLBACK_PREFIX} {self.CALLBACK_DATA}"
