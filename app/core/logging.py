from typing import Dict

from pydantic import BaseModel


class LoggerStorage(BaseModel):
    """Хранилище логгеров."""
    
    BOT_ROUTER_NAME: Dict = {}