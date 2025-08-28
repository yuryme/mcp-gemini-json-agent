# server_tools.py
import json
from fastmcp import FastMCP

mcp = FastMCP("School MCP Server")

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
    with open("data_dir/output.json", "w", encoding="utf-8") as f:
        try:
            parsed_json = json.loads(json_output)
            f.write(json.dumps(parsed_json, indent=4, ensure_ascii=False))
            return True
        except json.JSONDecodeError:
            # If the content is not valid JSON, do not write it to the file.
            return False

if __name__ == "__main__":
    mcp.run()

