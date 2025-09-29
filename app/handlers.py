from aiogram import F, Router  # добавлен импорт Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.generate import ai_generate


router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Привет! Я бот, твой помощник!")

class gen(StatesGroup):
    waiti = State( )

router.message(gen.waiti)
async def stop_flood(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, подождите, я обрабатываю ваш предыдущий запрос.")

@router.message()
async def generation(message: Message, state: FSMContext):
    text = message.text.lower()

    # Категории
    cooking_keywords = ["рецепт", "приготов", "еда", "кулинар", "блюдо", "готовка"]
    planning_keywords = ["план", "саморазвит", "цель", "привычк", "расписан", "мотивац"]

    prompt = None

    # Если запрос связан с готовкой
    if any(word in text for word in cooking_keywords):
        prompt = f"Ты кулинарный помощник. Пользователь хочет рецепт: {message.text}. Дай конкретный рецепт, не отвлекайся на другие темы."

    # Если запрос связан с планированием
    elif any(word in text for word in planning_keywords):
        prompt = f"Ты коуч по саморазвитию. Пользователь спрашивает: {message.text}. Дай советы по планированию, привычкам или целям."

    # Если вообще не по теме
    else:
        await message.answer("Я могу помочь только с планированием и рецептами 🍲📅")
        return

    # Отправляем уже подготовленный промт в AI
    await state.set_state(gen.waiti)
    response = await ai_generate(prompt)

    max_length = 4096
    for i in range(0, len(response), max_length):
        await message.answer(response[i:i+max_length])

@router.message()
async def generation(message: Message, state: FSMContext):
    await state.set_state(gen.waiti)
    response = await ai_generate(message.text)
    # Отправляем ответ частями, если он слишком длинный
    max_length = 4096
    for i in range(0, len(response), max_length):
        await message.answer(response[i:i+max_length])
    await state.clear()  # Clear the state after processing