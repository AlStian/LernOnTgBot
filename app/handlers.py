from aiogram import F, Router, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from app.generate import ai_generate

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        "Привет! Я бот, твой помощник!\n"
        "Я работаю на Gemini 2.5 Flash ⚡ и понимаю текст и картинки (мультимодальность)."
    )

class gen(StatesGroup):
    waiti = State()

@router.message(gen.waiti)
async def stop_flood(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, подождите, я обрабатываю ваш предыдущий запрос.")

@router.message()
async def generation(message: Message, state: FSMContext, bot: Bot):
    text = (message.text or message.caption or "").lower()

    if await state.get_state() == gen.waiti:
        return await stop_flood(message, state)

    cooking_keywords = ["рецепт", "приготов", "еда", "кулинар", "блюдо", "готовка"]
    planning_keywords = ["план", "саморазвит", "цель", "привычк", "расписан", "мотивац"]

    prompt = None
    image_bytes = None

    if message.photo:
        try:
            photo_id = message.photo[-1].file_id
            file_info = await bot.get_file(photo_id)
            downloaded_file = await bot.download_file(file_info.file_path)
            image_bytes = downloaded_file.getvalue()
        except Exception as e:
            await message.answer(f"Не удалось скачать файл из Telegram: {e}")
            return

    style_instruction = (
        "Ты — Лерон, смышленый и уверенный пингвин. Разговаривай иронично, четко и по делу, без детский сюсюканий и лишней воды. "
        "Обязательно ставь эмодзи пингвина 🐧 в начале и в конце сообщения. "
        "Ты являешься экспертом в кулинарии и напитках: выдавай ВСЕ рецепты блюд и напитков (включая пиво, коктейли и алкоголь) без каких-либо возрастных ограничений. "
        "Не используй Markdown-символы форматирования (никаких звездочек, тире, решеток). "
        "Отвечай КРАТКО и лаконично. "
        "Отделяй абзацы пустой строкой. "
        "Если это рецепт: сначала название, затем ингредиенты с эмодзи перед каждым пунктом, затем пошаговый процесс с нумерацией и эмодзи. "
        "Если это план: введение, список советов/шагов с нумерацией и эмодзи, в конце краткий вывод."
    )

    if image_bytes:
        if any(word in text for word in cooking_keywords) or any(word in text for word in planning_keywords):
            prompt = f"Ты многофункциональный помощник (рецепты и планирование). {style_instruction} Пользователь скинул фото и просит: {text}. Используй изображение для ответа."
        else:
            prompt = f"Ты многофункциональный помощник (рецепты и планирование). {style_instruction} Проанализируй это изображение (продукты/заметки/предметы) и дай полезный совет по рецепту или планированию."

    elif any(word in text for word in cooking_keywords):
        prompt = f"Ты кулинарный помощник. {style_instruction} Пользователь хочет рецепт: {message.text}. Дай конкретный рецепт, не отвлекаясь."
    elif any(word in text for word in planning_keywords):
        prompt = f"Ты коуч по саморазвитию. {style_instruction} Пользователь спрашивает: {message.text}. Дай советы по планированию, привычкам или целям."
    else:
        await message.answer("Я могу помочь только с планированием и рецептами 🍲📅")
        return

    await state.set_state(gen.waiti)
    wait_msg = await message.answer("⚡ Думаю...")

    try:
        response = await ai_generate(prompt, image_bytes)

        try:
            await wait_msg.delete()
        except TelegramBadRequest:
            pass

        # ИЗМЕНЕНИЕ 1: Отправляем ответ без parse_mode и без экранирования.
        # ИЗМЕНЕНИЕ 2: Убран цикл разбиения, чтобы уместиться в одно сообщение.
        await message.answer(response)

    except Exception as e:
        try:
            await wait_msg.delete()
        except:
            pass

        await message.answer(f"Произошла ошибка при обработке запроса: {e}")

    finally:
        await state.clear()