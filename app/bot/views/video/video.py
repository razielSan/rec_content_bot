from aiogram import Router, F
from aiogram.filters.state import StateFilter
from aiogram.types import Message

from bot.extension import models_settings
from app_utils.keyboards import get_total_buttons_inline_kb
from settings.response import messages
from core.response import InlineKeyboardData


router: Router = Router(
    name=models_settings.video_models.SERVICE_ID,
)


@router.message(
    StateFilter(None),
    F.text == models_settings.video_models.START_BOT_MENU_REPLY_TEXT,
)
async def video(message: Message) -> None:
    """
    Возвращает инлайн кнопки с варинтами выбора для раздела видео раздела.
    """
    await message.answer(
        text=messages.OPTIONS_BOT_MESSAGE,
        reply_markup=get_total_buttons_inline_kb(
            list_inline_kb_data=[
                InlineKeyboardData(
                    text=models_settings.video_models.CALLBACK_BUTTON_TEXT_VIEWING_ADVICE,
                    callback_data=models_settings.video_models.CALLBACK_BUTTON_DATA_VIEWING_ADVICE,
                ),
            ]
        ),
    )
