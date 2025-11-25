from bot.views.video.video import router as video_router
from bot.middleware.errors import RouterErrorMiddleware
from bot.extension import video_logger

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
