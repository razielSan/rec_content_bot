from bot.views.video.viewing_advice.main import router as video_viewing_advice_router
from bot.views.video.viewing_advice.kinopoisk import (
    router as video_viewing_advice_kinopoisk_router,
)
from bot.extension import video_logger
from bot.middleware.errors import RouterErrorMiddleware

video_viewing_advice_router.include_router(video_viewing_advice_kinopoisk_router)

video_viewing_advice_router.message.middleware(
    RouterErrorMiddleware(logger=video_logger.error_logger)
)
video_viewing_advice_router.callback_query.middleware(
    RouterErrorMiddleware(logger=video_logger.error_logger)
)
