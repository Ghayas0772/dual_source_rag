from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# -----------------------------
# CONFIG
# -----------------------------
endpoint = "https://gghayas6346-2931-resource.services.ai.azure.com/api/projects/gghayas6346-2931"

project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

client = project_client.get_openai_client()

agent_name = "dual-source-tutor-agent"
agent_version = "12"

# -----------------------------
# SAFE CALL
# -----------------------------
def call_agent(prompt):

    response = client.responses.create(
        input=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        extra_body={
            "agent_reference": {
                "type": "agent_reference",
                "name": agent_name,
                "version": agent_version
            }
        }
    )

    return response.output_text

# -----------------------------
# FILE TOOL
# -----------------------------
def file_tool(q):
    return {
        "tool": "file_tool",
        "input": q,
        "output": f"[FILE RESULT] {q}"
    }

# -----------------------------
# WEB TOOL
# -----------------------------
def web_tool(q):
    return {
        "tool": "web_tool",
        "input": q,
        "output": f"[WEB RESULT] {q}"
    }

# -----------------------------
# MEMORY TOOL
# -----------------------------
def memory_tool(q):
    return {
        "tool": "memory_tool",
        "input": q,
        "output": f"[MEMORY RESULT] {q}"
    }