import json
from datetime import datetime
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
def call_llm(prompt: str):
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
# NODE 1 — PLANNER
# -----------------------------
def planner(question):
    prompt = f"""
Route this question:

Return ONLY one word:
file, web, general

Question:
{question}
"""
    return call_llm(prompt).strip().lower()

# -----------------------------
# NODE 2 — TOOLS
# -----------------------------
def file_node(q):
    return call_llm(q)

def web_node(q):
    return call_llm(f"Use external knowledge:\n{q}")

def general_node(q):
    return call_llm(q)

# -----------------------------
# NODE 3 — MERGER (IMPORTANT NEW STEP)
# -----------------------------
def synthesizer(question, context):

    prompt = f"""
You are a reasoning engine.

Question:
{question}

Context:
{context}

Return:
- Definition
- Explanation
- Key Insight
"""
    return call_llm(prompt)

# -----------------------------
# NODE 4 — CRITIC (SCORE-BASED)
# -----------------------------
def critic(answer):

    prompt = f"""
Evaluate this answer strictly.

Return JSON ONLY:

{{
  "score": 0-10,
  "status": "ok" or "improve",
  "reason": "short reason"
}}

Answer:
{answer}
"""
    return call_llm(prompt)

# -----------------------------
# GRAPH EXECUTOR
# -----------------------------
def run_graph(question):

    print("\n================ PLANNER =================")
    route = planner(question)
    print("Route:", route)

    print("\n================ TOOL EXECUTION =================")

    if route == "file":
        context = file_node(question)

    elif route == "web":
        context = web_node(question)

    else:
        context = general_node(question)

    print(context)

    print("\n================ SYNTHESIS =================")
    answer = synthesizer(question, context)
    print(answer)

    print("\n================ CRITIC =================")
    verdict = critic(answer)
    print(verdict)

    # OPTIONAL LOOP LOGIC (simple version)
    if "improve" in verdict:
        print("\n🔁 Regenerating...\n")
        answer = synthesizer(question, context)
        print(answer)

    # SAVE TRACE
    trace = {
        "question": question,
        "route": route,
        "context": context,
        "answer": answer,
        "critic": verdict,
        "time": datetime.now().isoformat()
    }

    with open(f"trace_{datetime.now().timestamp()}.json", "w") as f:
        json.dump(trace, f, indent=2)

    return answer

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    q = input("Ask a question: ")
    run_graph(q)