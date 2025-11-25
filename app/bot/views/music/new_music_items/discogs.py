from datetime import datetime
import asyncio
from typing import Dict, List, Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InputMediaPhoto
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import aiohttp

from bot.extension import models_settings, music_logger, bot, get_button_start_bot_menu
from bot.functions.music.new_music import (
    get_list_albums_for_discogs,
    get_descripions_for_albums,
)
from app_utils.keyboards import (
    get_total_buttons_inline_kb,
    get_button_for_forward_or_back,
    get_reply_cancel_button,
)
from app_utils.fsm import async_make_update_progress
from error_handlers.decorator import safe_async_execution
from core.response import InlineKeyboardData, ResponseData
from settings.response import messages


router: Router = Router(
    name=models_settings.music_models.new_music.discogs.SERVICE_NAME,
)


class FSMNewMusicDiscogs(StatesGroup):
    """FSM для музыкальных новинок с сайта discogs.com."""

    data_state: State = State()
    albums_list: State = State()
    cancel: State = State()


@router.callback_query(
    StateFilter(None),
    F.data == models_settings.music_models.new_music.CALLBACK_BUTTON_DATA_DISCOGS,
)
async def discogs(call: CallbackQuery) -> None:
    """
    Возвращает пользователю инлайн клавиатуру с выбором возможных жанров для запроса.
    """
    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        text=messages.OPTIONS_BOT_MESSAGE,
        reply_markup=get_total_buttons_inline_kb(
            list_inline_kb_data=[
                InlineKeyboardData(
                    text=models_settings.music_models.new_music.discogs.DICT_STYLES.get(
                        "Punk"
                    ),
                    callback_data="nm_discogs+Punk",
                ),
                InlineKeyboardData(
                    text=models_settings.music_models.new_music.discogs.DICT_STYLES.get(
                        "Hardcore"
                    ),
                    callback_data="nm_discogs+Hardcore",
                ),
                InlineKeyboardData(
                    text=models_settings.music_models.new_music.discogs.DICT_STYLES.get(
                        "Crust"
                    ),
                    callback_data="nm_discogs+Crust",
                ),
                InlineKeyboardData(
                    text=models_settings.music_models.new_music.discogs.DICT_STYLES.get(
                        "Grindcore"
                    ),
                    callback_data="nm_discogs+Grindcore",
                ),
                InlineKeyboardData(
                    text=models_settings.music_models.new_music.discogs.DICT_STYLES.get(
                        "Post-Punk"
                    ),
                    callback_data="nm_discogs+Post-Punk",
                ),
                InlineKeyboardData(
                    text=models_settings.music_models.new_music.discogs.DICT_STYLES.get(
                        "Heavy Metal"
                    ),
                    callback_data="nm_discogs+Heavy Metal",
                ),
                InlineKeyboardData(
                    text=models_settings.music_models.new_music.discogs.DICT_STYLES.get(
                        "Thrash"
                    ),
                    callback_data="nm_discogs+Thrash",
                ),
                InlineKeyboardData(
                    text=models_settings.music_models.new_music.discogs.DICT_STYLES.get(
                        "Crossover thrash"
                    ),
                    callback_data="nm_discogs+Crossover thrash",
                ),
                InlineKeyboardData(
                    text=models_settings.music_models.new_music.discogs.DICT_STYLES.get(
                        "Black Metal"
                    ),
                    callback_data="nm_discogs+Black Metal",
                ),
                InlineKeyboardData(
                    text=models_settings.music_models.new_music.discogs.DICT_STYLES.get(
                        "Death Metal"
                    ),
                    callback_data="nm_discogs+Death Metal",
                ),
            ],
            quantity_button=2,
        ),
    )


@router.message(FSMNewMusicDiscogs.albums_list, F.text == "Отмена")
@router.message(FSMNewMusicDiscogs.cancel, F.text == "Отмена")
async def cancel_new_music_discogs_handler(message: Message, state: FSMContext) -> None:
    """
    Работа с FSMNewMusicDiscogs.

    Отменяет все действия.
    """
    current_state: Optional[str] = await state.get_state()

    # Если пользователь нажал кнопку отменя при обработке запроса на получние музыкальных новинок
    if current_state == "FSMNewMusicDiscogs:cancel":
        await state.set_state(FSMNewMusicDiscogs.cancel)
        await state.update_data(cancel=True)
        return

    await state.clear()
    await bot.send_message(
        chat_id=message.chat.id,
        text=messages.CANCEL_MESSAGE,
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer(
        text=messages.START_BOT_MESSAGE,
        reply_markup=get_button_start_bot_menu,
    )


@router.message(FSMNewMusicDiscogs.albums_list, F.text)
async def get_message_for_albums_list_new_music_discogs_handler(
    message: Message, state: FSMContext
) -> None:
    """
    Работа с FSMNewMusicDiscogs.

    Отправляет пользователю сообщение если он ввел текст когда уже музыкальные новинки
    были отображены.
    """
    await message.reply(text=messages.MENU_CANCEL_MESSAGE)


@router.message(FSMNewMusicDiscogs.cancel, F.text)
async def get_message_for_cancel_new_music_discogs_handler(
    message: Message, state: FSMContext
) -> None:
    """
    Работа с FSMNewMusicDiscogs.

    Отправляет пользователю сообщение если он ввел текст при обработке
    запроса на получние музыкальных новинок.
    """
    await message.reply(text=messages.WAIT_AND_CANCEL_MESSAGE)


@router.callback_query(F.data.startswith("nm_discogs+"))
async def get_album_artists_by_genre_for_site_discogs(
    call: CallbackQuery, state: FSMContext, session: aiohttp.ClientSession
) -> None:
    """Возвращает найденных исполнителей для discogs и кнопки назад и вперед."""
    await call.message.delete_reply_markup()

    # Встаем в состояние cancel для того чтобы отправлять сообщение пользователю если
    # он ввел текст при запросе и для отмены запроса
    await state.set_state(FSMNewMusicDiscogs.cancel)

    await bot.send_message(
        chat_id=call.message.chat.id,
        text=messages.WAIT_LONG_RESPONSE_MESSAGE.format(
            start=0,
            end=5,
        ),
        reply_markup=get_reply_cancel_button(),
    )
    # Получаем жанр, год и необходимое количество альбомов для поиске
    _, genre = call.data.split("+")
    year: int = datetime.now().year
    total_count_album: int = (
        models_settings.music_models.new_music.discogs.COUNT_ALBUMS_SEARCH
    )

    # Функция для отслеживания прогресса
    update_progress = async_make_update_progress(state=state)

    # Оборочиваем функцию в декоратор для отлова всех возможных ошибок
    decorator_funtion = safe_async_execution(
        logging_data=music_logger,
    )
    func = decorator_funtion(get_list_albums_for_discogs)

    # Формируем Task для отслеживания прогресса и возможности отмены задачи
    progress_task = asyncio.create_task(
        func(
            genre,
            total_count_album,
            models_settings.music_models.new_music.discogs.URL_SEARCH,
            year,
            update_progress,
            models_settings.music_models.new_music.discogs,
            session,
            music_logger,
        )
    )

    # Формируем сообщение пользователю во время обработки запроса
    progress_message: Message = await call.message.answer(
        text=messages.RESPONSE_WAIT_MESSAGE.format(percent=0)
    )

    # Текущий прогресс скачивания
    current_progress: int = 0

    # Встаем в цикл пока Task не завершится
    while not progress_task.done():
        data: Dict = await state.get_data()

        # если пользователь нажал кнопку отмены
        if data.get("cancel", None):
            progress_task.cancel()

            # позволяем task завершится корректно
            try:
                await progress_task
            except asyncio.CancelledError:
                pass
            # Выходим из цикла
            break

        digit: int = data.get("data_state", 0)  # сколько альбомов загружено
        percent: int = round((digit / total_count_album) * 100)  # количество прогресса
        # в процентах
        try:
            # Обновляем прогресс если не равны
            if percent != current_progress:
                await progress_message.edit_text(
                    text=messages.RESPONSE_WAIT_MESSAGE.format(percent=percent)
                )
                current_progress = percent
        except Exception as err:
            print(err)
        await asyncio.sleep(2)

    # Получаем все альбомы
    data = await progress_task

    # Проверяем на состояние отмены
    cancel: Dict = await state.get_data()
    if cancel.get("cancel", None):

        # Отправляем пользователю сообщения для ожидания отмены всех задач
        await bot.send_message(
            chat_id=call.message.chat.id,
            text=messages.BUTTON_CANCEL_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
        )

        # Ждем пока отменятся все таски чтобы корректно сделать state.clear
        while not progress_task.done():
            await bot.send_chat_action(call.message.chat.id, "typing")
            await asyncio.sleep(0.5)

        await state.clear()
        await bot.send_message(
            chat_id=call.message.chat.id,
            text=messages.CANCEL_MESSAGE,
        )
        await call.message.answer(
            text=messages.START_BOT_MESSAGE,
            reply_markup=get_button_start_bot_menu,
        )
    else:
        # Проверяем что запрос прошел успешно
        if data.message:

            album_artist: Dict = data.message[0].dict()  # достаем первый альбом
            img: str = album_artist["IMG"]  # url картинки

            result: ResponseData = get_descripions_for_albums(
                album_artist
            )  # описание альбома
            album: str = result.message

            await bot.send_message(
                chat_id=call.message.chat.id,
                text=messages.END_RESPONSE_MESSAGE,
            )
            # Ставим на засыпание чтобы пользователь сперва увидел сообщение о загрузке
            await asyncio.sleep(1)

            await bot.send_photo(
                chat_id=call.message.chat.id,
                photo=img,
                caption=album,
                reply_markup=get_button_for_forward_or_back(
                    list_albums=album_artist, count=0, step=1, prefix="discogs"
                ),
            )
            await bot.send_message(
                chat_id=call.message.chat.id,
                text=messages.MENU_CANCEL_MESSAGE,
            )
            # Встаем в состояние albums_list для дальнейшего пролистывания албомов
            await state.set_state(FSMNewMusicDiscogs.albums_list)
            await state.update_data(albums_list=data.message)
        else:
            await state.clear()
            await bot.send_message(chat_id=call.message.chat.id, text=str(data.error))
            await call.message.answer(
                text=messages.START_BOT_MESSAGE,
                reply_markup=get_button_start_bot_menu,
            )


@router.callback_query(FSMNewMusicDiscogs.albums_list, F.data.startswith("discogs"))
async def leafing_through_albums(call: CallbackQuery, state: FSMContext):
    """Листает альбомы назад и вперед."""
    data: Dict = await state.get_data()

    # Получаем данные об альбоме
    _, button, count = call.data.split(" ")
    albums_list: List = data["albums_list"]
    album: Dict = albums_list[int(count)].dict()
    img: str = album["IMG"]

    description_album: ResponseData = get_descripions_for_albums(
        album
    )  # описание альбома

    await bot.edit_message_media(
        media=InputMediaPhoto(media=img, caption=description_album.message),
        message_id=call.message.message_id,
        chat_id=call.message.chat.id,
        reply_markup=get_button_for_forward_or_back(
            count=int(count), list_albums=albums_list, prefix="discogs"
        ),
    )
