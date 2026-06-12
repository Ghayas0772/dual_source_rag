import json
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

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
# PLANNER
# -----------------------------
def planner(q):
    return call(f"""
Route question into:
file, web, general

Question:
{q}
""").strip().lower()

# -----------------------------
# SPECIALIZED AGENTS
# -----------------------------
def file_agent(q):
    return call(f"Use internal documents:\n{q}")

def web_agent(q):
    return call(f"Use external knowledge:\n{q}")

def general_agent(q):
    return call(q)

# -----------------------------
# SYNTHESIZER
# -----------------------------
def synthesizer(q, outputs):

    prompt = f"""
You are a senior AI system.

Question:
{q}

Agent Outputs:
FILE:
{outputs.get('file')}

WEB:
{outputs.get('web')}

GENERAL:
{outputs.get('general')}

Create ONE best final answer:
- Definition
- Explanation
- Key Insight
"""
    return call(prompt)

# -----------------------------
# CRITIC A (ACCURACY)
# -----------------------------
def critic_accuracy(answer):
    return call(f"""
Evaluate accuracy only.

Return JSON:
{{
 "score": 0-10,
 "comment": ""
}}

Answer:
{answer}
""")

# -----------------------------
# CRITIC B (CLARITY)
# -----------------------------
def critic_clarity(answer):
    return call(f"""
Evaluate clarity only.

Return JSON:
{{
 "score": 0-10,
 "comment": ""
}}

Answer:
{answer}
""")

# -----------------------------
# EXECUTION ENGINE
# -----------------------------
def run(q):

    print("\n================ PLANNER ================\n")
    route = planner(q)
    print("Route:", route)

    outputs = {}

    print("\n================ AGENT EXECUTION ================\n")

    outputs = {}

    if route == "file":
    outputs["file"] = file_agent(q)

    elif route == "web":
    outputs["web"] = web_agent(q)

    else:
    outputs["general"] = general_agent(q)
    outputs["file"] = file_agent(q)
    outputs["web"] = web_agent(q)
    outputs["general"] = general_agent(q)

    print("\n================ SYNTHESIS ================\n")
    final = synthesizer(q, outputs)
    print(final)

    print("\n================ CRITICS ================\n")

    a = critic_accuracy(final)
    b = critic_clarity(final)

    print("Accuracy:", a)
    print("Clarity:", b)

    # -----------------------------
    # SAVE TRACE
    # -----------------------------
    trace = {
        "question": q,
        "route": route,
        "outputs": outputs,
        "final": final,
        "critic_a": a,
        "critic_b": b,
        "timestamp": datetime.now().isoformat()
    }

    file = f"trace_{datetime.now().timestamp()}.json"
    with open(file, "w") as f:
        json.dump(trace, f, indent=2)

    print("\n📁 Trace saved:", file)

    return final

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    q = input("Ask a question: ")
    run(q)