from typing import List

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types.keyboard_button import KeyboardButton
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from core.response import InlineKeyboardData


def get_total_buttons_inline_kb(
    list_inline_kb_data: List[InlineKeyboardData],
    quantity_button: int = 1,
    resize_keyboard: bool = True,
) -> InlineKeyboardMarkup:
    """Общая inline клавиатура с генерацими кнопок.

    Args:
        list_inline_kb_data (List[InlineKeyboardData]): список из InlineKeyboardData с данными о кнопке
        quantity_button (int): Количество кнопок на строке(По умолчанию 1)
        resize_keyboard (bool, optional): Изменяет размер клавиатуры по вертикали для оптимального размещения

    Returns:
        InlineKeyboardMarkup: Возвращает инлайн клавиатуру
    """
    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()

    for button in list_inline_kb_data:
        inline_kb.add(
            InlineKeyboardButton(
                text=button.text,
                callback_data=button.callback_data,
            )
        )
    inline_kb.adjust(quantity_button)
    return inline_kb.as_markup(resize_keyboard=resize_keyboard)


def get_total_buttons_reply_kb(
    list_text: List[str],
    quantity_button: int,
    resize_keyboard=True,
) -> ReplyKeyboardMarkup:
    """Общая reply клавиатура с генерацими кнопок.

    Args:
        list_text (List[str]): Список из строк с названиями кнопок
        quantity_button (int): Количество кнопок на строке
        resize_keyboard (bool, optional): Изменяет размер клавиатуры по вертикали для оптимального размещения

    Returns:
        ReplyKeyboardMarkup: Возвращает reply клавиатуру
    """
    reply_kb: ReplyKeyboardBuilder = ReplyKeyboardBuilder()

    for text_button in list_text:
        reply_kb.add(KeyboardButton(text=text_button))

    reply_kb.adjust(quantity_button)

    return reply_kb.as_markup(
        resize_keyboard=resize_keyboard,
    )


def get_reply_cancel_button() -> ReplyKeyboardMarkup:
    """Reply кнопка отмены."""
    reply_kb: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    reply_kb.add(KeyboardButton(text="Отмена"))
    return reply_kb.as_markup(resize_keyboard=True)
