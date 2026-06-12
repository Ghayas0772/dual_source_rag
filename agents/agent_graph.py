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
# GRAPH STATE
# -----------------------------
class GraphState:
    def __init__(self):
        self.question = None
        self.route = None
        self.context = None
        self.answer = None
        self.verdict = None


# -----------------------------
# PLANNER
# -----------------------------
def planner(question):

    prompt = f"""
You are a router.

Decide best source.

Return ONLY one word:
file, web, general

Question:
{question}
"""

    res = client.responses.create(
        input=[{"role": "user", "content": prompt}],
        extra_body={
            "agent_reference": {
                "name": agent_name,
                "version": agent_version,
                "type": "agent_reference"
            }
        }
    )

    route = res.output_text.strip().lower()

    if "file" in route:
        return "file"
    elif "web" in route:
        return "web"
    else:
        return "general"


# -----------------------------
# FILE AGENT (RAG)
# -----------------------------
def file_agent(question):

    res = client.responses.create(
        input=[{"role": "user", "content": question}],
        extra_body={
            "agent_reference": {
                "name": agent_name,
                "version": agent_version,
                "type": "agent_reference"
            }
        }
    )

    return res.output_text


# -----------------------------
# WEB AGENT (SIMULATED)
# -----------------------------
def web_agent(question):

    prompt = f"""
Use external knowledge.

Explain clearly:

{question}
"""

    res = client.responses.create(
        input=[{"role": "user", "content": prompt}],
        extra_body={
            "agent_reference": {
                "name": agent_name,
                "version": agent_version,
                "type": "agent_reference"
            }
        }
    )

    return res.output_text


# -----------------------------
# GENERAL REASONING
# -----------------------------
def general_agent(question):

    res = client.responses.create(
        input=[{"role": "user", "content": question}],
        extra_body={
            "agent_reference": {
                "name": agent_name,
                "version": agent_version,
                "type": "agent_reference"
            }
        }
    )

    return res.output_text


# -----------------------------
# ANSWER GENERATOR (SYNTHESIS)
# -----------------------------
def answer_generator(context):

    prompt = f"""
Create a structured answer:

Context:
{context}

Format:
- Definition
- Explanation
- Key Insight
"""

    res = client.responses.create(
        input=[{"role": "user", "content": prompt}],
        extra_body={
            "agent_reference": {
                "name": agent_name,
                "version": agent_version,
                "type": "agent_reference"
            }
        }
    )

    return res.output_text


# -----------------------------
# VALIDATOR (CRITIC AGENT)
# -----------------------------
def validator(answer):

    prompt = f"""
Evaluate answer.

Return ONLY:
OK or REGENERATE

Answer:
{answer}
"""

    res = client.responses.create(
        input=[{"role": "user", "content": prompt}],
        extra_body={
            "agent_reference": {
                "name": agent_name,
                "version": agent_version,
                "type": "agent_reference"
            }
        }
    )

    return res.output_text.strip().upper()


# -----------------------------
# RUN GRAPH
# -----------------------------
def run_agent(question):

    state = GraphState()
    state.question = question

    print("\n================ PLANNER =================\n")

    state.route = planner(question)
    print("Route:", state.route)

    # -----------------------------
    # ROUTING
    # -----------------------------
    print("\n================ CONTEXT =================\n")

    if state.route == "file":
        state.context = file_agent(question)

    elif state.route == "web":
        state.context = web_agent(question)

    else:
        state.context = general_agent(question)

    print(state.context)

    # -----------------------------
    # GENERATION
    # -----------------------------
    state.answer = answer_generator(state.context)

    print("\n================ ANSWER =================\n")
    print(state.answer)

    # -----------------------------
    # VALIDATION LOOP
    # -----------------------------
    state.verdict = validator(state.answer)

    print("\n================ VALIDATION =================\n")
    print(state.verdict)

    if "REGENERATE" in state.verdict:
        print("\n🔁 Regenerating...\n")

        improved_context = state.answer
        state.answer = answer_generator(improved_context)

        print(state.answer)

    return state.answer


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":

    q = input("Ask a question: ")
    run_agent(q)