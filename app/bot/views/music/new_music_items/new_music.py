from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.filters.state import StateFilter

from bot.extension import models_settings
from app_utils.keyboards import get_total_buttons_inline_kb
from core.response import InlineKeyboardData
from settings.response import messages


router = Router(
    name=models_settings.music_models.new_music.SERVICE_NAME,
)


@router.callback_query(
    StateFilter(None),
    F.data == models_settings.music_models.CALLBACK_BUTTON_DATA_NEW_MUSIC,
)
async def music(call: CallbackQuery):

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        text=messages.OPTIONS_BOT_MESSAGE,
        reply_markup=get_total_buttons_inline_kb(
            list_inline_kb_data=[
                InlineKeyboardData(
                    text=models_settings.music_models.new_music.CALLBACK_BUTTON_TEXT_DISCOGS,
                    callback_data=models_settings.music_models.new_music.CALLBACK_BUTTON_DATA_DISCOGS,
                )
            ]
        ),
    )
