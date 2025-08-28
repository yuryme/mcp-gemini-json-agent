# server_tools.py
import json
import os
import re
from fastmcp import FastMCP

mcp = FastMCP("School MCP Server")

OUTPUT_PATH = "data_dir/output.json"

def _normalize_json_text(s: str) -> str:
    """
    Делает строку пригодной для json.loads:
    - убирает ограждение ```json ... ```
    - вырезает оболочку до первых/последних { } или [ ]
    """
    if not isinstance(s, str):
        return ""
    s = s.strip()
    m = re.search(r"```(?:json)?\s*(.*?)\s*```", s, flags=re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()

    # Объект
    l, r = s.find("{"), s.rfind("}")
    if l != -1 and r != -1 and r > l:
        return s[l : r + 1].strip()

    # Массив
    l, r = s.find("["), s.rfind("]")
    if l != -1 and r != -1 and r > l:
        return s[l : r + 1].strip()

    return s

@mcp.tool
def echo(text: str) -> str:
    return text

@mcp.resource("data://input")
def input_text() -> str:
    with open("data_dir/input.json", "r", encoding="utf-8") as f:
        return f.read()

@mcp.resource("data://types")
def data_types_text() -> str:
    with open("data_dir/data_types.json", "r", encoding="utf-8") as f:
        return f.read()

@mcp.resource("data://object_uid")
def object_uid_text() -> str:
    with open("data_dir/object_uid.json", "r", encoding="utf-8") as f:
        return f.read()

@mcp.tool
def write_json_output(json_output: str) -> bool:
    """
    Пишет валидный JSON в data_dir/output.json. Если json_output невалидный — возвращает False.
    """
    # 1) Нормализуем и валидируем
    raw = _normalize_json_text(json_output)
    try:
        parsed_json = json.loads(raw)
    except json.JSONDecodeError:
        return False

    # 2) Гарантируем наличие каталога
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # 3) Пишем красиво, без потери Unicode
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(parsed_json, indent=4, ensure_ascii=False))
    return True

if __name__ == "__main__":
    mcp.run()
    