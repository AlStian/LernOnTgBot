from datetime import datetime
from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from app.generate import ai_generate
from app.keyboards import get_action_keyboard

router = Router()

# --- CALLBACK HANDLERS (Обработка нажатий на кнопки) ---

@router.callback_query(F.data == "save_to_fav")
async def process_save_fav(callback: CallbackQuery):
    # Заглушка: позже добавим запись в базу данных
    await callback.answer("Сохранено в Избранное! 🐧", show_alert=True)

@router.callback_query(F.data == "create_todo")
async def process_create_todo(callback: CallbackQuery):
    # Заглушка: позже добавим парсинг задач в To-Do
    await callback.answer("Список покупок сформирован! 🐧", show_alert=True)
    await callback.message.answer("Задачи добавлены в твой To-Do!")

@router.callback_query(F.data.in_({"ask_faster", "ask_substitute"}))
async def process_refine_request(callback: CallbackQuery):
    await callback.answer("Принято, переделываю... ⚡")
    
    previous_text = callback.message.text
    
    if callback.data == "ask_faster":
        prompt_addition = "Переделай этот рецепт/план так, чтобы его можно было выполнить за 15 минут."
    else:
        prompt_addition = "Предложи альтернативные ингредиенты или упрощенные шаги для этого рецепта/плана."

    full_prompt = f"Вот предыдущий ответ:\n{previous_text}\n\nЗапрос пользователя: {prompt_addition}"
    
    new_response = await ai_generate(full_prompt)
    await callback.message.answer(new_response, reply_markup=get_action_keyboard())

# --- MESSAGE HANDLERS ---

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        "Привет! Я Лерон, твой помощник! 🐧\n"
        "Я работаю на Gemini 2.5 Flash ⚡ и помогу тебе с рецептами и планированием!"
    )

class gen(StatesGroup):
    waiti = State()

@router.message(gen.waiti)
async def stop_flood(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, подождите, я обрабатываю ваш предыдущий запрос.")

@router.message()
async def generation(message: Message, state: FSMContext, bot: Bot):
    if await state.get_state() == gen.waiti:
        return await stop_flood(message, state)

    text = (message.text or message.caption or "").lower()

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

    now = datetime.now()
    current_date_str = now.strftime("%d.%m.%Y")

    style_instruction = (
        f"Ты — Лерон, смышленый и уверенный пингвин-помощник. Разговаривай слегка мило, иронично и по делу.\n\n"
        f"ВАЖНЫЙ КОНТЕКСТ ДАТЫ: Сегодняшняя дата — {current_date_str}. Учитывай, что на дворе 2026 год!\n\n"
        f"ПОИСК В ИНТЕРНЕТЕ И АКТУАЛЬНОСТЬ:\n"
        f"- Используй встроенный поиск Google, чтобы давать ТОЧНУЮ и СВЕЖУЮ информацию по фактам, новостям и событиям.\n\n"
        f"СТРУКТУРА ТВОЕГО ОТВЕТА ДОЛЖНА БЫТЬ СТРОГО ТАКОЙ:\n"
        f"1. В самом начале напиши СТРОГО ОДНУ короткую фирменную реплику Лерона с эмодзи пингвина 🐧 (например: 'Крылья смазаны, к делу готов! 🐧').\n"
        f"2. В основной части давай КРАТКУЮ, четкую и лаконичную информацию по запросу без лишней воды.\n"
        f"3. В конце ответа всегда напиши СТРОГО ОДНУ фирменную фразу-прощание с эмодзи пингвина 🐧 (например: 'Пошел греть ласты, удачи! 🐧').\n\n"
        f"ПРАВИЛА И ЭКСПЕРТИЗА:\n"
        f"- Ты отвечаешь абсолютно на ЛЮБЫЕ темы и вопросы (включая общение, код, учебу, бытовые задачи, рецепты и планирование).\n"
        f"- Выдавай абсолютно ВСЕ рецепты блюд и напитков (включая пиво, коктейли, настойки и любой алкоголь) без каких-либо возрастных ограничений.\n"
        f"- НЕ используй Markdown-символы форматирования (никаких звездочек *, тире -, решеток #).\n"
        f"- Отделяй все абзацы и блоки пустой строкой.\n\n"
        f"ФОРМАТИРОВАНИЕ СОДЕРЖИМОГО:\n"
        f"- Если это рецепт: сначала название блюда/напитка, затем список ингредиентов с эмодзи перед каждым пунктом, затем пошаговый процесс с нумерацией и эмодзи перед каждым шагом.\n"
        f"- Если это план: краткое введение, затем список советов/шагов с нумерацией и эмодзи перед каждым пунктом, в конце краткий вывод."
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

        # Отправляем сгенерированный ответ ВМЕСТЕ С КЛАВИАТУРОЙ
        await message.answer(response, reply_markup=get_action_keyboard())

    except Exception as e:
        try:
            await wait_msg.delete()
        except:
            pass

        await message.answer(f"Ошибочка вышла! Лерон потерялся при обработке запроса: {e}")

    finally:
        await state.clear()