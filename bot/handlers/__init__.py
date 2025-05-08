from .start import start_router
from .registration import registration_router

def register_handlers(dp):
    dp.include_router(start_router)
    dp.include_router(registration_router)

