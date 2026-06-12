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
# ROUTER PROMPT
# -----------------------------
router_prompt = """
You are a routing system.

Decide tool type:

- file → internal documents
- web → external/latest info
- reasoning → general knowledge

Return ONLY one word:
file, web, reasoning
"""

# -----------------------------
# ROUTER FUNCTION
# -----------------------------
def route_question(question):

    response = client.responses.create(
        input=[
            {"role": "user", "content": router_prompt + "\n\nQUESTION:\n" + question}
        ],
        extra_body={
            "agent_reference": {
                "name": agent_name,
                "version": agent_version,
                "type": "agent_reference"
            }
        }
    )

    route = response.output_text.strip().lower()

    print("\n================ ROUTER RAW OUTPUT ================\n")
    print(route)

    if "file" in route:
        return "file"
    elif "web" in route:
        return "web"
    else:
        return "reasoning"
# -----------------------------
# EXECUTION FUNCTION
# -----------------------------
def run_router_agent(question):

    print("\n================ QUESTION ================\n")
    print(question)

    route = route_question(question)

    print("\n================ FINAL ROUTE ================\n")
    print(route)

    # -----------------------------
    # EXECUTE (SIMPLIFIED)
    # -----------------------------
    response = client.responses.create(
        input=[{"role": "user", "content": question}],
        extra_body={
            "agent_reference": {
                "name": agent_name,
                "version": agent_version,
                "type": "agent_reference"
            }
        }
    )

    answer = response.output_text

    print("\n================ ANSWER ================\n")
    print(answer)

    return {
        "question": question,
        "route": route,
        "answer": answer
    }

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":

    q = input("Ask a question: ")

    result = run_router_agent(q)

    print("\n================ FINAL OUTPUT OBJECT ================\n")
    print(result)