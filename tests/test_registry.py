# test_registry.py

from tool_registry import register_tool, get_tool, list_tools

def hello():
    return "Hello"

register_tool("hello_tool", hello)

print(list_tools())

tool = get_tool("hello_tool")

print(tool())