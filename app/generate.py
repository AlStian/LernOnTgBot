import google.generativeai as genai
from config import AI_TOKEN
import PIL.Image
import io

# 1. КОНФИГУРАЦИЯ
# Настраиваем доступ к Gemini
genai.configure(api_key=AI_TOKEN)

# 2. ВЫБОР МОДЕЛИ
# Внедряем Gemini 2.5 Flash
model_name = "gemini-2.5-flash"
model = genai.GenerativeModel(model_name)
# Настройки генерации контента
config = genai.types.GenerationConfig(
    max_output_tokens=500,  # Задаем максимальный лимит токенов
    temperature=0.8         # Можно снизить, например, до 0.5, чтобы ответы были менее креативными и более прямолинейными
)
# 3. ФУНКЦИЯ ГЕНЕРАЦИИ (поддерживает текст Изображение)
async def ai_generate(text: str, image_bytes: bytes = None):
    try:
        content = []
        
        # Обрабатываем изображение, если оно передано
        if image_bytes:
            # Преобразуем байты в объект PIL Image, который нужен Gemini
            image = PIL.Image.open(io.BytesIO(image_bytes))
            content.append(image)
            
        # Добавляем текст-запрос
        if text:
            content.append(text)
        
        if not content:
            return "Нечего анализировать."

        # Асинхронная генерация контента
        response = await model.generate_content_async(content)
        
        if response.text:
            return response.text
        else:
            return "Нейросеть не вернула текстовый ответ (возможно, запрос нарушил политику)."
            
    except Exception as e:
        error_message = str(e)
        print(f"Ошибка Gemini API ({model_name}): {error_message}")
        
        # Удобные сообщения об ошибках для пользователя
        if "404" in error_message or "not found" in error_message.lower():
            return f"Ошибка: Модель {model_name} недоступна. Попробуйте 'gemini-1.5-flash'."
        if "429" in error_message:
             return "Ошибка: Вы превысили бесплатный лимит запросов. Попробуйте позже."
        return "Произошла техническая ошибка при запросе к нейросети."