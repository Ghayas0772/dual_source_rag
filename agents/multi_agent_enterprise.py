import json
import asyncio
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
Route:
file, web, general

Question:
{q}
""").strip().lower()

# -----------------------------
# AGENTS (SIMULATED PARALLEL)
# -----------------------------
async def file_agent(q):
    return call(f"Use internal documents:\n{q}")

async def web_agent(q):
    return call(f"Use web knowledge:\n{q}")

async def general_agent(q):
    return call(q)

# -----------------------------
# SYNTHESIZER
# -----------------------------
def synthesizer(q, outputs):

    prompt = f"""
Merge all agent outputs into one answer:

Question:
{q}

FILE:
{outputs['file']}

WEB:
{outputs['web']}

GENERAL:
{outputs['general']}

Return structured answer:
- Definition
- Explanation
- Key Insight
"""
    return call(prompt)

# -----------------------------
# VOTERS (SCORING SYSTEM)
# -----------------------------
def voter_accuracy(answer):
    return call(f"""
Score accuracy 0-10:

Answer:
{answer}
Return JSON:
{{"score": number}}
""")

def voter_clarity(answer):
    return call(f"""
Score clarity 0-10:

Answer:
{answer}
Return JSON:
{{"score": number}}
""")

# -----------------------------
# FINAL DECISION ENGINE
# -----------------------------
def decide(final_answer, a_score, b_score):

    prompt = f"""
Decide final quality.

Answer:
{final_answer}

Accuracy Score:
{a_score}

Clarity Score:
{b_score}

Return:
BEST or REWRITE
"""
    return call(prompt)

# -----------------------------
# EXECUTION ENGINE (REAL PARALLEL)
# -----------------------------
async def run(q):

    print("\n================ PLANNER ================\n")
    route = planner(q)
    print("Route:", route)

    print("\n================ PARALLEL AGENTS ================\n")

    outputs = await asyncio.gather(
        file_agent(q),
        web_agent(q),
        general_agent(q)
    )

    context = {
        "file": outputs[0],
        "web": outputs[1],
        "general": outputs[2]
    }

    print("\n================ SYNTHESIS ================\n")
    final = synthesizer(q, context)
    print(final)

    print("\n================ VOTING SYSTEM ================\n")

    a = voter_accuracy(final)
    b = voter_clarity(final)

    print("Accuracy:", a)
    print("Clarity:", b)

    print("\n================ DECISION ENGINE ================\n")

    decision = decide(final, a, b)
    print("Decision:", decision)

    trace = {
        "question": q,
        "route": route,
        "context": context,
        "final": final,
        "accuracy": a,
        "clarity": b,
        "decision": decision,
        "time": datetime.now().isoformat()
    }

    file = f"trace_{datetime.now().timestamp()}.json"
    with open(file, "w") as f:
        json.dump(trace, f, indent=2)

    print("\n📁 Trace saved:", file)

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    q = input("Ask a question: ")
    asyncio.run(run(q))