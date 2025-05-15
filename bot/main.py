import asyncio
import logging 
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from bot.config import BOT_TOKEN
from bot.handlers import register_handlers
from database.models import init_db
init_db()
#логирование, которые будет предупреждать об ошибках и выводить все данные о этой ошибки.
logging.basicConfig(
    level = logging.INFO, 
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__) 
logger.info("Бот запущен!")
bot = Bot(token=BOT_TOKEN,default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
register_handlers(dp)

async def main():
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())