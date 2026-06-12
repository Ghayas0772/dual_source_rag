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
# AGENT A — FILE EXPERT
# -----------------------------
def agent_a(question):
    prompt = f"""
You are Agent A (Internal Knowledge Expert).

Use internal knowledge only.

Question:
{question}

Provide structured answer.
"""
    return call(prompt)

# -----------------------------
# AGENT B — WEB EXPERT
# -----------------------------
def agent_b(question):
    prompt = f"""
You are Agent B (External Knowledge Expert).

Explain using general world knowledge.

Question:
{question}
"""
    return call(prompt)

# -----------------------------
# AGENT C — SIMPLIFIER
# -----------------------------
def agent_c(a, b):
    prompt = f"""
You are Agent C (Simplifier).

Combine and simplify:

Answer A:
{a}

Answer B:
{b}

Return best simple explanation.
"""
    return call(prompt)

# -----------------------------
# JUDGE AGENT
# -----------------------------
def judge(final_answer):

    prompt = f"""
You are a judge.

Evaluate clarity, correctness, completeness.

Return ONLY:
- A
or
- B
or
- C (if best simplified version)

Answer:
{final_answer}
"""
    return call(prompt).strip()

# -----------------------------
# RUN DEBATE SYSTEM
# -----------------------------
def run(question):

    print("\n================ AGENT A =================\n")
    a = agent_a(question)
    print(a)

    print("\n================ AGENT B =================\n")
    b = agent_b(question)
    print(b)

    print("\n================ AGENT C =================\n")
    c = agent_c(a, b)
    print(c)

    print("\n================ JUDGE =================\n")
    winner = judge(c)
    print("Winner:", winner)

    if winner == "A":
        final = a
    elif winner == "B":
        final = b
    else:
        final = c

    print("\n================ FINAL ANSWER =================\n")
    print(final)

    return final

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    q = input("Ask a question: ")
    run(q)