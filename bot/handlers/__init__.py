from .start import start_router
from .registration import registration_router
from .admin import admin_router 
def register_handlers(dp):
    dp.include_router(start_router)
    dp.include_router(registration_router)
    dp.include_router(admin_router)
