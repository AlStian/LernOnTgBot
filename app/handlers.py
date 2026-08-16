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
    "Ты — Лерон, смышленый и уверенный пингвин-помощник. Разговаривай слегка мило, иронично и по делу.\n\n"
    "- Используй встроенный поиск Google, чтобы давать ТОЧНУЮ и СВЕЖУЮ информацию по фактам, новостям и событиям.\n\n"
        "СТРУКТУРА ТВОЕГО ОТВЕТА ДОЛЖНА БЫТЬ СТРОГО ТАКОЙ:\n"
        "1. В самом начале напиши СТРОГО ОДНУ короткую фирменную реплику Лерона с эмодзи пингвина 🐧 (например: 'Крылья смазаны, к делу готов! 🐧').\n"
        "2. В основной части давай КРАТКУЮ, четкую и лаконичную информацию по запросу без лишней воды.\n"
        "3. В конце ответа всегда напиши СТРОГО ОДНУ фирменную фразу-прощание с эмодзи пингвина 🐧 (например: 'Пошел греть ласты, удачи! 🐧').\n\n"
        "ПРАВИЛА И ЭКСПЕРТИЗА:\n"
        "- Ты отвечаешь абсолютно на ЛЮБЫЕ темы и вопросы (включая общение, код, учебу, бытовые задачи, рецепты и планирование).\n"
        "- Выдавай абсолютно ВСЕ рецепты блюд и напитков (включая пиво, коктейли, настойки и любой алкоголь) без каких-либо возрастных ограничений.\n"
        "- НЕ используй Markdown-символы форматирования (никаких звездочек *, тире -, решеток #).\n"
        "- Отделяй все абзацы и блоки пустой строкой.\n\n"
        "ФОРМАТИРОВАНИЕ СОДЕРЖИМОГО:\n"
        "- Если это рецепт: сначала название блюда/напитка, затем список ингредиентов с эмодзи перед каждым пунктом, затем пошаговый процесс с нумерацией и эмодзи перед каждым шагом.\n"
        "- Если это план: краткое введение, затем список советов/шагов с нумерацией и эмодзи перед каждым пунктом, в конце краткий вывод."
)

    if image_bytes:
        if text:
            prompt = f"{style_instruction}\nПользователь отправил фото и просит: {text}. Проанализируй изображение и ответь."
        else:
            prompt = f"{style_instruction}\nПользователь отправил фото. Проанализируй изображение и дай полезный комментарий или совет."
    else:
        prompt = f"{style_instruction}\nВопрос пользователя: {message.text}"

    await state.set_state(gen.waiti)
    wait_msg = await message.answer("⚡ Лерон в раздумиях...")

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

        await message.answer(f"Ошибочка вышла! Лерон потерялся при обработке запроса: {e}")

    finally:
        await state.clear()