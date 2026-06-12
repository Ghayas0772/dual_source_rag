import json
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

from memory_system import build_context, add_memory

# -----------------------------
# CONFIG
# -----------------------------
endpoint = "https://gghayas6346-2931-resource.services.ai.azure.com/api/projects/gghayas6346-2931"

client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
).get_openai_client()

agent_name = "dual-source-tutor-agent"
agent_version = "12"

# -----------------------------
# SAFE CALL
# -----------------------------
def call(prompt):
    return client.responses.create(
        input=[{"role": "user", "content": prompt}],
        extra_body={
            "agent_reference": {
                "type": "agent_reference",
                "name": agent_name,
                "version": agent_version
            }
        }
    ).output_text

# -----------------------------
# PLANNER (MEMORY-AWARE)
# -----------------------------
def planner(context):

    prompt = f"""
You are a routing agent.

Use user context if helpful.

Decide:
file, web, general

CONTEXT:
{context}

Return only one word.
"""
    return call(prompt).strip().lower()

# -----------------------------
# AGENTS
# -----------------------------
def file_agent(context):
    return call(f"Use internal docs:\n{context}")

def web_agent(context):
    return call(f"Use external knowledge:\n{context}")

def general_agent(context):
    return call(context)

# -----------------------------
# SYNTHESIZER
# -----------------------------
def synthesizer(question, outputs, context):

    prompt = f"""
You are a senior AI system.

USER CONTEXT:
{context}

QUESTION:
{question}

FILE OUTPUT:
{outputs['file']}

WEB OUTPUT:
{outputs['web']}

GENERAL OUTPUT:
{outputs['general']}

Return:
- Definition
- Explanation
- Key Insight
"""
    return call(prompt)

# -----------------------------
# CRITIC
# -----------------------------
def critic(answer):

    prompt = f"""
Evaluate answer.

Return ONLY:
OK or REGENERATE

Answer:
{answer}
"""
    return call(prompt).strip().upper()

# -----------------------------
# GRAPH RUNNER
# -----------------------------
def run(question):

    # 🧠 STEP 1 — LOAD MEMORY CONTEXT
    context = build_context(question)

    print("\n================ MEMORY CONTEXT ================\n")
    print(context)

    # 🧠 STEP 2 — ROUTING
    print("\n================ PLANNER ================\n")
    route = planner(context)
    print("Route:", route)

    # 🧠 STEP 3 — TOOL EXECUTION
    if route == "file":
        outputs = {
            "file": file_agent(context),
            "web": "",
            "general": ""
        }

    elif route == "web":
        outputs = {
            "file": "",
            "web": web_agent(context),
            "general": ""
        }

    else:
        outputs = {
            "file": "",
            "web": "",
            "general": general_agent(context)
        }

    # 🧠 STEP 4 — SYNTHESIS
    print("\n================ SYNTHESIS ================\n")
    answer = synthesizer(question, outputs, context)
    print(answer)

    # 🧠 STEP 5 — CRITIC
    print("\n================ CRITIC ================\n")
    verdict = critic(answer)
    print(verdict)

    # 🧠 STEP 6 — MEMORY SAVE
    add_memory(question, answer)

    print("\n💾 Memory updated")

    return answer

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    q = input("Ask a question: ")
    run(q)