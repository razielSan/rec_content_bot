from typing import Tuple, Optional, List
from pathlib import Path
from logging import Logger


def ensure_derictories(
    *args: Path,
    info_logger: Optional[Logger] = None,
) -> None:
    """
    Проверяет наличие переданных путей и создает их при необходимости.

    Args:
        info_logger (Optional[Logger], optional): Логгер для записи в лог. Defaults to None.
    """
    requiered_dirs: Tuple[Path, ...] = args

    for dir in requiered_dirs:
        dir.mkdir(parents=True, exist_ok=True)
        if info_logger:
            info_logger.info(f"Директория {dir} созданна")


def delete_data(
    list_path: List[Path],
    warning_logger: Optional[Logger] = None,
) -> None:
    """Удаляет данные по переданному пути.

    Args:
        path (Path): Список с путями до данных
        warning_logger (Optional[Logger], optional): логгер для записи в лог(По умолчанию None)
    """
    for path in list_path:
        try:
            if path.exists():
                path.unlink()
        except Exception as err:
            message: str = f"Ошибка при удалении {path}: {err}"
            if warning_logger:
                warning_logger.exception(msg=message)
