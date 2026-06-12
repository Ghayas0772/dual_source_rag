# tool_registry.py

TOOLS = {}

def register_tool(name, func):
    """
    Register a tool in the registry
    """
    TOOLS[name] = func


def get_tool(name):
    """
    Return a tool by name
    """
    return TOOLS.get(name)


def list_tools():
    """
    Return all registered tool names
    """
    return list(TOOLS.keys())