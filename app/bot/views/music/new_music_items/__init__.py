from bot.views.music.new_music_items.new_music import router as new_music_router
from bot.views.music.new_music_items.discogs import router as new_music_discogs_router


new_music_router.include_router(new_music_discogs_router)
