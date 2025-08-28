# --- глушим DeprecationWarning и фикс для Windows ---
import warnings, sys, asyncio
warnings.filterwarnings("ignore", category=DeprecationWarning)
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# ----------------------------------------------------

import os
from dotenv import load_dotenv
import google.generativeai as genai
from fastmcp import Client

def setup_gemini():
    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    return genai.GenerativeModel("gemini-2.5-flash")

def ask_gemini(model, prompt: str) -> str:
    resp = model.generate_content(prompt)
    return (resp.text or "").strip()

def build_prompt(user_question: str, input_txt: str, types_txt: str, object_uid_txt: str) -> str:
    return (

        "Ты — ассистент, который может отвечать на вопросы пользователя на основе контекста и справки.\n"
        "Ты отлично разбираешься в структуре JSON и умеешь модифицировать JSON по описанию.\n"
        "В контексте имеется JSON, описывающий объект метаданных в Web приложении для автоматизации бизнеса.\n"
        " Приложение имеет конструктор, позволяющий описывать структуру объектов метаданных при помощи JSON\n"
        " и модифицировать их через импорт JSON описывающего новую структуру объекта. Измени JSON так,\n"
        " как просит пользователь \n"
        "используй информацию из контекста и справки.\n"
        "Контекст из файла data_dir/input.txt:\n"
        f"{input_txt}\n"
        "Доп. справка из data_dir/data_types.txt:\n"
        f"{types_txt}\n"
       # "Доп. справка из data_dir/object_uid.json:\n"
       #f"{object_uid_txt}\n"
        "Задание: ответь на вопрос пользователя, в ответе только JSON, без текста, без лишних символов. Когда пользователь просит совершить действия с объектами метаданных он имеет ввиду создание или редактирование JSON, описывающего этот объект\n"
        f"Вопрос: {user_question}"
    )

async def read_resource_text(client: Client, uri: str) -> str:
    contents = await client.read_resource(uri)
    return "\n".join(getattr(c, "text", "") for c in contents if getattr(c, "text", None))

async def main_async():
    model = setup_gemini()
    client = Client("server_tools.py")

    async with client:
        # одноразовый вопрос из аргументов
        if len(sys.argv) > 1:
            q = " ".join(sys.argv[1:])
            input_txt = await read_resource_text(client, "data://input")
            types_txt = await read_resource_text(client, "data://types")
            object_uid_txt = await read_resource_text(client, "data://object_uid")
            print(ask_gemini(model, build_prompt(q, input_txt, types_txt, object_uid_txt)))
            return

        # интерактив — один общий цикл событий без повторных asyncio.run(...)
        print("Введи вопрос (пустая строка — выход).")
        while True:
            q = input("\nВаш вопрос: ").strip()
            if not q:
                print("Пока!")
                break
            input_txt = await read_resource_text(client, "data://input")
            types_txt = await read_resource_text(client, "data://types")
            object_uid_txt = await read_resource_text(client, "data://object_uid")
            print(ask_gemini(model, build_prompt(q, input_txt, types_txt, object_uid_txt)))

if __name__ == "__main__":
    asyncio.run(main_async())
