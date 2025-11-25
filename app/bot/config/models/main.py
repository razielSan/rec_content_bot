from pathlib import Path
from bot.config.models.music import MusicModels
from bot.config.models.video import VideoModels

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseGeneration(BaseSettings):
    """Общий класс для генерации моделей."""

    music_models: MusicModels = MusicModels()
    video_models: VideoModels = VideoModels()

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        extra="ignore",
        env_nested_delimiter="__",
    )
