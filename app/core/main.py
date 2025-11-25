from pathlib import Path

from pydantic import BaseModel


class AppSettings(BaseModel):
    """Общие настроцки для всего приложения."""

    BOT_ROOT_NAME: str = "root_bot"

    # Базовые пути - вычисляются относительно этого файла
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent
    PATH_LOG_FOLDER: Path = ROOT_DIR / "logs"

    # Различные форматы записей
    LOG_FORMAT: str = (
        "[%(asctime)s] - %(module)s:%(lineno)s - [%(levelname)s - %(message)s]"
    )
    DATE_FORMAT: str = "%Y-%m-%D %H-%M-%S"
