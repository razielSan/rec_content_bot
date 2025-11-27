from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.filters.state import StateFilter

from bot.extension import models_settings
from app_utils.keyboards import get_total_buttons_inline_kb
from settings.response import messages
from core.response import InlineKeyboardData

router: Router = Router(name=models_settings.video_models.viewing_advice.SERVICE_ID)


@router.callback_query(
    StateFilter(None),
    F.data == models_settings.video_models.CALLBACK_BUTTON_DATA_VIEWING_ADVICE,
)
async def viewing_advice(call: CallbackQuery) -> None:
    """Возвращает инлайн кнопки с варинтами выбора для совета по названию фильма."""
    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        text=messages.OPTIONS_BOT_MESSAGE,
        reply_markup=get_total_buttons_inline_kb(
            list_inline_kb_data=[
                InlineKeyboardData(
                    text=models_settings.video_models.viewing_advice.CALLBACK_BUTTON_TEXT_KINOPOISK,
                    callback_data=models_settings.video_models.viewing_advice.CALLBACK_BUTTON_DATA_KINOPOISK,
                )
            ],
        ),
    )
