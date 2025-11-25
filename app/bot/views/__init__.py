from bot.views.main import router as main_router
from bot.views.music import music_router
from bot.views.video import video_router
from bot.middleware.errors import RouterErrorMiddleware
from bot.extension import main_logger


main_router.include_router(music_router)
main_router.include_router(video_router)


main_router.message.middleware(
    RouterErrorMiddleware(
        logger=main_logger.error_logger,
    )
)

main_router.callback_query.middleware(
    RouterErrorMiddleware(
        logger=main_logger.error_logger,
    )
)
