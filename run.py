import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher

from app.handlers import router
from config import TG_TOKEN


# Функция-заглушка для хелсчека Render
async def handle_ping(request):
    return web.Response(text="Лерон работает!")


async def main():
    # 1. Настраиваем микро веб-сервер для Render
    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)

    runner = web.AppRunner(app)
    await runner.setup()

    # Берем порт, который дает Render (по умолчанию 10000)
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Веб-сервер запущен на порту {port}")

    # 2. Твоя привычная логика запуска Лерона
    bot = Bot(token=TG_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Лерон уснул, бот остановлен')