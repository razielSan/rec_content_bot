from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.state import StateFilter

from bot.extension import get_button_start_bot_menu, bot_settings, models_settings
from settings.response import messages


router = Router(
    name=bot_settings.BOT_NAME,
)


@router.message(
    StateFilter(None),
    F.text == "/start",
)
async def main(message: Message):
    await message.answer(
        text=messages.START_BOT_MESSAGE,
        reply_markup=get_button_start_bot_menu,
    )
