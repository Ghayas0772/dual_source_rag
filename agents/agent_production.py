import json
from datetime import datetime

import tools.tool_setup as tool_setup  # ensures tools are registered
from tool_registry import get_tool

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
# MEMORY
# -----------------------------
MEMORY_FILE = "memory.json"

def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_memory(entry):
    memory = load_memory()
    memory.append(entry)

    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

# -----------------------------
# TRACE LOG
# -----------------------------
trace_log = []
TRACE_FILE = f"trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

def log(step, data):
    trace_log.append({
        "step": step,
        "data": data,
        "time": datetime.now().isoformat()
    })

# -----------------------------
# LLM CALL WRAPPER
# -----------------------------
def call_llm(messages):
    return client.responses.create(
        input=messages,
        extra_body={
            "agent_reference": {
                "type": "agent_reference",
                "name": agent_name,
                "version": agent_version
            }
        }
    ).output_text

# -----------------------------
# PLANNER (ROUTER)
# -----------------------------
def planner(question):

    prompt = f"""
You are a router.

Return ONLY one tool name:

file_tool
web_tool
memory_tool

Question:
{question}
"""

    route = call_llm([
        {"role": "user", "content": prompt}
    ]).strip().lower()

    valid_tools = {"file_tool", "web_tool", "memory_tool"}

    if route not in valid_tools:
        return "file_tool"

    return route

# -----------------------------
# SYNTHESIS
# -----------------------------
def synthesize(context):

    prompt = f"""
Create a structured answer:

Context:
{context}

Format:
- Definition
- Explanation
- Key Insight
"""

    return call_llm([{"role": "user", "content": prompt}])

# -----------------------------
# CRITIC
# -----------------------------
def critic(answer):

    prompt = f"""
Evaluate the answer.

Return ONLY:
OK or REGENERATE

Answer:
{answer}
"""

    verdict = call_llm([{"role": "user", "content": prompt}]).strip().upper()

    if "REGENERATE" in verdict:
        return "REGENERATE"

    return "OK"

# -----------------------------
# MAIN PIPELINE
# -----------------------------
def run(question):

    log("input", question)

    # MEMORY
    memory = load_memory()
    log("memory", memory)

    # ROUTING
    route = planner(question)
    log("route", route)

    print("\n================ ROUTE =================\n")
    print("Selected Tool:", route)

    # TOOL EXECUTION
    tool = get_tool(route)

    if tool:
        print(f"\nExecuting Tool: {route}")
        raw_result = tool(question)
    else:
        print("\nTool not found, fallback used")
        raw_result = question

    log("tool_used", route)
    log("tool_output", raw_result)

    # NORMALIZE CONTEXT
    if isinstance(raw_result, dict):
        context = raw_result.get("output", str(raw_result))
    else:
        context = raw_result

    log("context", context)

    # SYNTHESIS
    answer = synthesize(context)
    log("answer", answer)

    # CRITIC
    verdict = critic(answer)
    log("verdict", verdict)

    print("\n================ VERDICT =================\n")
    print(verdict)

    # LOOP
    if verdict == "REGENERATE":
        print("\n🔁 Regenerating...\n")
        answer = synthesize(context)
        log("regenerated_answer", answer)

    # SAVE MEMORY
    save_memory({
        "question": question,
        "answer": answer,
        "time": datetime.now().isoformat()
    })

    # SAVE TRACE
    with open(TRACE_FILE, "w") as f:
        json.dump(trace_log, f, indent=2)

    # FINAL OUTPUT
    print("\n================ FINAL ANSWER ================\n")
    print(answer)

    print("\nTRACE SAVED:", TRACE_FILE)


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    q = input("Ask a question: ")
    run(q)
    
    print("\nDEBUG TOOL OBJECT:", tool)