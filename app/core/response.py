from typing import Optional, Any
from dataclasses import dataclass
from logging import Logger

from pydantic import BaseModel


class ResponseData(BaseModel):
    """Модель для возвращаения ответов."""

    error: Optional[str] = None
    message: Optional[Any] = None
    url: Optional[str] = None
    status: Optional[int] = None
    method: Optional[str] = None


@dataclass
class LoggingData:
    """Модель для возврата логгеров."""

    info_logger: Logger
    warning_logger: Logger
    error_logger: Logger
    router_name: Logger


class InlineKeyboardData(BaseModel):
    """Модель для инлайн клавиатуры."""

    text: str
    callback_data: str
    resize_keyboard: Optional[bool] = True
