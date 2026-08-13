import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TG_TOKEN
from app.handlers import router

# Включаем логирование, чтобы видеть ошибки в консоли
logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=TG_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот остановлен')