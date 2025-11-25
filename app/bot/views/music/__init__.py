from bot.views.music.music import router as music_router
from bot.views.music.new_music_items import new_music_router
from bot.middleware.errors import RouterErrorMiddleware
from bot.extension import music_logger


music_router.include_router(new_music_router)


music_router.message.middleware(
    RouterErrorMiddleware(
        logger=music_logger.error_logger,
    )
)

music_router.callback_query.middleware(
    RouterErrorMiddleware(
        logger=music_logger.error_logger,
    )
)
