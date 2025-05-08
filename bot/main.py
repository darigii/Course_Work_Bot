import asyncio
import logging 
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from bot.config import BOT_TOKEN
#логирование, которые будет предупреждать об ошибках и выводить все данные о этой ошибки.
logging.basicConfig()(
    level = logging.INFO, 
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__) 
logger.info("Бот запущен!")
