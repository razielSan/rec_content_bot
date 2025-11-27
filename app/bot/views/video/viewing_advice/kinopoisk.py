from typing import Dict, List, Optional
from random import shuffle

from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    ReplyKeyboardRemove,
    FSInputFile,
    InputMediaPhoto,
)
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import aiohttp


from bot.extension import models_settings, get_button_start_bot_menu, bot, video_logger
from bot.functions.video.viewing_advice import (
    get_recommender_video_for_kinopoisk,
    get_description_video_from_kinopoisk,
)
from core.response import ResponseData
from app_utils.keyboards import get_reply_cancel_button, get_button_for_forward_or_back
from settings.response import messages
from error_handlers.network import error_handler_for_the_website
from error_handlers.decorator import safe_async_execution

router: Router = Router(
    name=models_settings.video_models.viewing_advice.kinopoisk.SERVICE_ID,
)


class FSMVideoKinopoisk(StatesGroup):
    spam: State = State()
    description: State = State()
    recommender_list: State() = State()


@router.callback_query(
    StateFilter(None),
    F.data
    == models_settings.video_models.viewing_advice.CALLBACK_BUTTON_DATA_KINOPOISK,
)
async def kinopoisk(call: CallbackQuery, state: FSMContext) -> None:
    """
    Работа с FSMVideoKinopoisk.

    Просит у пользователя ввести название фильма для рекомендации.
    """

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        "🔎 Введите название фильма, для которого хотите найти похожие фильмы",
        reply_markup=get_reply_cancel_button(),
    )

    await state.set_state(FSMVideoKinopoisk.description)


@router.message(FSMVideoKinopoisk.description, F.text == "Отмена")
@router.message(FSMVideoKinopoisk.recommender_list, F.text == "Отмена")
async def cancel_viewing_advice_kinopoisk(message: Message, state: FSMContext) -> None:
    """
    Работа с FSMVideoKinopoisk.

    Отменяет все действия.
    """
    await state.clear()
    await message.answer(
        text=messages.CANCEL_MESSAGE,
        reply_markup=ReplyKeyboardRemove(),
    )
    await bot.send_message(
        chat_id=message.chat.id,
        text=messages.START_BOT_MESSAGE,
        reply_markup=get_button_start_bot_menu,
    )


@router.message(FSMVideoKinopoisk.recommender_list, F.text)
@router.message(FSMVideoKinopoisk.spam, F.text)
async def get_message_by_kinopoisk(message: Message, state: FSMContext) -> None:
    """
    Отправляет пользователю сообщение при вводе текста во время запроса.

    Отправляем сообщение при вводе текса при пролистывании фильмов.
    """
    current_state: Optional[str] = await state.get_state()

    print(current_state, 11)
    if current_state == "FSMVideoKinopoisk:recommender_list":
        await message.reply(text=messages.MENU_CANCEL_MESSAGE)
        return

    await message.reply(text=messages.WAIT_MESSAGE)


@router.message(FSMVideoKinopoisk.description, F.text)
async def get_data_recominder(
    message: Message,
    state: FSMContext,
    session: aiohttp.ClientSession,
) -> None:
    """
    Работа с FSM RecomenderSystemFSM.

    Возвращает рекомендации для https://www.kinopoisk.ru/.
    """

    await state.set_state(FSMVideoKinopoisk.spam)

    await message.answer(
        text=messages.WAIT_MESSAGE,
        reply_markup=ReplyKeyboardRemove(),
    )

    headers: Dict = models_settings.video_models.viewing_advice.kinopoisk.HEADERS
    headers["X-API-KEY"] = models_settings.video_models.viewing_advice.kinopoisk.API_KEY

    video_name: ResponseData = await error_handler_for_the_website(
        session=session,
        url=models_settings.video_models.viewing_advice.kinopoisk.URL_SEARCH_VIDEO_NAME.format(
            limit=10,
            name=message.text,
        ),
        logging_data=video_logger,
        function_name=get_data_recominder.__name__,
        headers=headers,
        timeout=30,
    )
    if video_name.message:
        # Проверка на наличие фильмов по запросу для рекомендации
        result: List = video_name.message.get("docs")
        if not result:
            await state.set_state(FSMVideoKinopoisk.description)
            await message.answer(
                text=f"🔎 Фильм для составления рекомендации не был"
                f" найденн\n\n{messages.TRY_REPSONSE_MESSAGE}"
            )
        else:
            json_kinopoisk: Dict = result[0]

            # Получаем url с лимитом видео для поиска
            url: str = models_settings.video_models.viewing_advice.kinopoisk.URL_SEARCH_UNIVERSAL_VIDEO.format(
                limit=250
            )

            decorator_function = safe_async_execution(logging_data=video_logger)
            func = decorator_function(get_recommender_video_for_kinopoisk)

            # Делает первый запрос с рейтингом 1-5
            recommender_video_list_1: ResponseData = await func(
                session,
                url,
                json_kinopoisk.get("genres"),
                25,
                json_kinopoisk.get("type"),
                "6-10",
                headers,
                video_logger,
                30,
            )

            # Если произошел TIMEOUT_ERROR пробуем делать запрос с  меньшей выборкой
            error = recommender_video_list_1.error
            if error == messages.TIMEOUT_ERROR:
                url: str = models_settings.video_models.viewing_advice.kinopoisk.URL_SEARCH_UNIVERSAL_VIDEO.format(
                    limit=10
                )

                decorator_function = safe_async_execution(logging_data=video_logger)
                func = decorator_function(get_recommender_video_for_kinopoisk)

                recommender_video_list_1: ResponseData = await func(
                    session,
                    url,
                    json_kinopoisk.get("genres"),
                    25,
                    json_kinopoisk.get("type"),
                    "6-10",
                    headers,
                    video_logger,
                    30,
                )

            if recommender_video_list_1.message:
                decorator_function = safe_async_execution(logging_data=video_logger)
                func = decorator_function(get_recommender_video_for_kinopoisk)

                # Делает второй запрос с рейтингом 6-10
                recommender_video_list_2: ResponseData = await func(
                    session,
                    url,
                    json_kinopoisk.get("genres"),
                    25,
                    json_kinopoisk.get("type"),
                    "1-5",
                    headers,
                    video_logger,
                    30,
                )
                # Состваляет общий рекомендательный список
                recommender_video_list: List = []

                # Если второй запрос выдал ошибку составляем рекомендацию по первому запросу
                if recommender_video_list_2.error:
                    pass
                else:
                    recommender_video_list.extend(recommender_video_list_2.message)
                recommender_video_list.extend(recommender_video_list_1.message)

                # Перемешивает список
                shuffle(recommender_video_list)

                # Получаем описание видео
                description_video: ResponseData = get_description_video_from_kinopoisk(
                    data=recommender_video_list[0],
                )

                # Получаем обложку к фильму
                poster = recommender_video_list[0].get("poster", 0)
                # Проверяет есть ли фотография в данных
                photo: str = ""
                if poster:
                    photo = recommender_video_list[0]["poster"].get("url", 0)

                if photo:
                    await bot.send_photo(
                        chat_id=message.chat.id,
                        photo=photo,
                        caption=description_video.message,
                        reply_markup=get_button_for_forward_or_back(
                            prefix="kinopoisk",
                            list_albums=recommender_video_list,
                            count=0,
                            step=1,
                        ),
                    )
                else:

                    await bot.send_photo(
                        chat_id=message.chat.id,
                        photo=FSInputFile(
                            path=models_settings.video_models.viewing_advice.kinopoisk.PATH_TO_FILENAME_DEFOLTE_IMAGE_KINOPOISK,
                        ),
                        caption=description_video.message,
                        reply_markup=get_button_for_forward_or_back(
                            prefix="kinopoisk",
                            list_albums=recommender_video_list,
                            count=0,
                            step=1,
                        ),
                    )

                await bot.send_message(
                    chat_id=message.chat.id,
                    text=messages.MENU_CANCEL_MESSAGE,
                    reply_markup=get_reply_cancel_button(),
                )
                await state.set_state(FSMVideoKinopoisk.recommender_list)
                await state.update_data(recommender_list=recommender_video_list)
            else:
                await state.set_state(FSMVideoKinopoisk.description)
                await message.answer(
                    f"{recommender_video_list_1.error}\n\n{messages.TRY_REPSONSE_MESSAGE}",
                    reply_markup=get_reply_cancel_button(),
                )

    else:
        await state.set_state(FSMVideoKinopoisk.description)
        await message.answer(
            f"{video_name.error}\n\n{messages.TRY_REPSONSE_MESSAGE}",
            reply_markup=get_reply_cancel_button(),
        )


@router.callback_query(
    FSMVideoKinopoisk.recommender_list, F.data.startswith("kinopoisk")
)
async def scrolls_through_the_list_of_recommendations(
    call: CallbackQuery,
    state: FSMContext,
) -> None:
    """
    Работа с FSM RecomenderSystemFSM.

    Пролистывает видео по результатам кинопоиска.
    """
    _, _, count = call.data.split(" ")
    data: Dict = await state.get_data()
    recommender_list = data["recommender_list"]

    description: ResponseData = get_description_video_from_kinopoisk(
        data=recommender_list[int(count)],
    )

    poster = recommender_list[int(count)].get("poster", 0)

    photo: str = ""
    if poster:
        photo = recommender_list[int(count)]["poster"].get("url", 0)

    if photo:
        # Проверяем подойдет ли фото если нет грузим страндартное
        try:
            await bot.edit_message_media(
                media=InputMediaPhoto(media=photo, caption=description.message),
                message_id=call.message.message_id,
                chat_id=call.message.chat.id,
                reply_markup=get_button_for_forward_or_back(
                    prefix="kinopoisk",
                    list_albums=recommender_list,
                    count=int(count),
                ),
            )
        except Exception:
            await bot.edit_message_media(
                media=InputMediaPhoto(
                    media=FSInputFile(
                        path=models_settings.video_models.viewing_advice.kinopoisk.PATH_TO_FILENAME_DEFOLTE_IMAGE_KINOPOISK,
                    ),
                    caption=description.message,
                ),
                message_id=call.message.message_id,
                chat_id=call.message.chat.id,
                reply_markup=get_button_for_forward_or_back(
                    prefix="kinopoisk",
                    list_albums=recommender_list,
                    count=int(count),
                ),
            )

    else:
        await bot.edit_message_media(
            media=InputMediaPhoto(
                media=FSInputFile(
                    path=models_settings.video_models.viewing_advice.kinopoisk.PATH_TO_FILENAME_DEFOLTE_IMAGE_KINOPOISK,
                ),
                caption=description,
            ),
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            reply_markup=get_button_for_forward_or_back(
                prefix="kinopoisk",
                list_albums=recommender_list,
                count=int(count),
            ),
        )
