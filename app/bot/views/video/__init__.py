from bot.views.video.video import router as video_router
from bot.views.video.viewing_advice import video_viewing_advice_router
from bot.middleware.errors import RouterErrorMiddleware
from bot.extension import video_logger


video_router.include_router(video_viewing_advice_router)

video_router.message.middleware(
    RouterErrorMiddleware(
        logger=video_logger.error_logger,
    )
)

video_router.callback_query.middleware(
    RouterErrorMiddleware(
        logger=video_logger.error_logger,
    )
)
