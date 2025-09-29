from openai import AsyncOpenAI
from config import AI_TOKEN

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=AI_TOKEN,
)

async def ai_generate(text: str):
    completion = await client.chat.completions.create(
        model="deepseek/deepseek-chat-v3.1:free",
        messages=[
            {
                "role": "system",
                "content": (
                    "Ты ассистент с двумя функциями: "
                    "1) Даёшь рецепты еды, когда спрашивают про готовку. "
                    "2) Помогаешь с планированием и саморазвитием. "
                    "На другие темы не отвечаешь."
                )
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content