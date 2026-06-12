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
# 🧠 PLANNER
# -----------------------------
def planner(question):

    prompt = f"""
You are a planner agent.

Decide best strategy:

Options:
- file_tool
- web_tool
- memory_tool
- direct_answer

Question:
{question}

Return only one option.
"""
    return call(prompt).strip().lower()

# -----------------------------
# 🔧 TOOL EXECUTOR
# -----------------------------
def file_tool(q):
    return call(f"Use internal files:\n{q}")

def web_tool(q):
    return call(f"Use web knowledge:\n{q}")

def memory_tool(q):
    return call(f"Use past knowledge:\n{q}")

# -----------------------------
# 🧠 REASONING AGENT
# -----------------------------
def reason(question, context):

    prompt = f"""
You are a reasoning agent.

Question:
{question}

Context:
{context}

Create a structured answer:
- Definition
- Explanation
- Example
- Key insight
"""
    return call(prompt)

# -----------------------------
# ⚖️ VERIFIER
# -----------------------------
def verifier(answer):

    prompt = f"""
Check correctness and clarity.

If good → OK
If bad → FIX

Answer:
{answer}
"""
    return call(prompt).strip().upper()

# -----------------------------
# 🔁 LOOP CONTROLLER
# -----------------------------
def run(question):

    print("\n================ PLANNER =================\n")
    route = planner(question)
    print("Route:", route)

    # -------------------------
    # TOOL EXECUTION
    # -------------------------
    if route == "file_tool":
        context = file_tool(question)

    elif route == "web_tool":
        context = web_tool(question)

    elif route == "memory_tool":
        context = memory_tool(question)

    else:
        context = question

    print("\n================ CONTEXT =================\n")
    print(context)

    # -------------------------
    # REASONING
    # -------------------------
    print("\n================ REASONING =================\n")
    answer = reason(question, context)
    print(answer)

    # -------------------------
    # VERIFICATION LOOP
    # -------------------------
    print("\n================ VERIFIER =================\n")
    verdict = verifier(answer)
    print("Verdict:", verdict)

    # -------------------------
    # SELF-CORRECTION LOOP
    # -------------------------
    if "FIX" in verdict:
        print("\n🔁 Regenerating improved answer...\n")
        answer = reason(question, context)

    print("\n================ FINAL ANSWER =================\n")
    print(answer)

    return answer

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    q = input("Ask a question: ")
    run(q)