from tool_registry import register_tool

from tools import (
    file_tool,
    web_tool,
    memory_tool
)

# -----------------------------
# REGISTER TOOLS
# -----------------------------
register_tool("file_tool", file_tool)

register_tool("web_tool", web_tool)

register_tool("memory_tool", memory_tool)

print("Tools Registered Successfully")