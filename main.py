import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher

from app.handlers import router
from config import TG_TOKEN  # Импортируем TG_TOKEN из config.py


# --- Заглушка для Render ---
async def handle_root(request):
    return web.Response(text="Лерон бот работает!")


async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_root)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render сам передаст порт в переменную окружения PORT (по умолчанию 8080)
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Веб-сервер запущен на порту {port}")


# --- Основная логика бота ---
async def main():
    # Запускаем фоновый веб-сервер, чтобы Render увидел открытый порт
    await start_web_server()

    bot = Bot(token=TG_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Лерон уснул, бот остановлен')
