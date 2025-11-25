import traceback
from typing import Optional, Any
from logging import Logger

from aiogram import BaseMiddleware


class RouterErrorMiddleware(BaseMiddleware):
    """Middleware для обработки ошибок routera."""

    def __init__(self, logger: Logger, global_logger=None) -> None:
        """Инициализация параметров."""
        super().__init__()
        self.global_logger: Optional[Logger] = global_logger
        self.current_logger: Logger = logger

    async def __call__(self, handler, event, data) -> Optional[Any]:
        """Обработчик ошибок."""
        try:
            return await handler(event, data)
        except Exception as err:
            # Формируем красивое сообщение
            error_text: str = (
                f"🚨 Ошибка в Router: {self.current_logger.name}\n"
                f"Тип события: {type(event).__name__}\n"
                f"Пользователь: {getattr(event.from_user, 'username', 'Неизвестно')} "
                f"(id={getattr(event.from_user, 'id', '—')})\n"
                f"Текст: {getattr(event, 'text', '—')}\n"
                f"Ошибка: {err}\n"
                f"Трассировка:\n{traceback.format_exc()}"
                f"\n{'-' * 80}\n"
            )

            # Логируем локально
            self.current_logger.error(error_text)
            # Логируем глобально, если есть
            if self.global_logger:
                self.global_logger.error(error_text)