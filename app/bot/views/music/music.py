from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.state import StateFilter

from bot.extension import models_settings
from app_utils.keyboards import get_total_buttons_inline_kb
from core.response import InlineKeyboardData
from settings.response import messages


router = Router(
    name=models_settings.music_models.SERVICE_NAME,
)


@router.message(
    StateFilter(None),
    F.text == models_settings.music_models.START_BOT_MENU_REPLY_TEXT,
)
async def music(message: Message):
    print(models_settings.music_models.CALLBACK_BUTTON_DATA_NEW_MUSIC)
    await message.answer(
        text=messages.OPTIONS_BOT_MESSAGE,
        reply_markup=get_total_buttons_inline_kb(
            list_inline_kb_data=[
                InlineKeyboardData(
                    text=models_settings.music_models.CALLBACK_BUTTON_TEXT_NEW_MUSIC,
                    callback_data=models_settings.music_models.CALLBACK_BUTTON_DATA_NEW_MUSIC,
                )
            ]
        ),
    )
