import asyncio
from aiogram import Bot, Dispatcher

from app.handlers import router


from config import TG_TOKEN  # Импортируем TG_TOKEN из config.py

async def main(): 
    bot = Bot(token=TG_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот остановлен')
