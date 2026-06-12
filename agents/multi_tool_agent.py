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
# ROUTER
# -----------------------------
def router(question):

    prompt = """
Decide tool:

file → internal documents
web → external latest info
reasoning → general knowledge

Return ONLY one word: file, web, reasoning
"""

    response = client.responses.create(
        input=[
            {"role": "user", "content": prompt + "\n\nQUESTION:\n" + question}
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

    print("\nROUTE:", route)

    if "file" in route:
        return "file"
    elif "web" in route:
        return "web"
    else:
        return "reasoning"

# -----------------------------
# TOOL: FILE
# -----------------------------
def file_search(question):
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
    return response.output_text

# -----------------------------
# TOOL: WEB
# -----------------------------
def web_search(question):
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
    return response.output_text

# -----------------------------
# TOOL: REASONING
# -----------------------------
def reasoning(question):
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
    return response.output_text

# -----------------------------
# SYNTHESIS LAYER
# -----------------------------
def synthesize(question, tool_output, tool_used):

    prompt = f"""
You are a synthesis agent.

Question:
{question}

Tool used:
{tool_used}

Tool output:
{tool_output}

Now produce a clean final answer with:
- Definition
- Explanation
- Key insight
"""

    response = client.responses.create(
        input=[{"role": "user", "content": prompt}],
        extra_body={
            "agent_reference": {
                "name": agent_name,
                "version": agent_version,
                "type": "agent_reference"
            }
        }
    )

    return response.output_text

# -----------------------------
# MAIN AGENT FLOW
# -----------------------------
def run_agent(question):

    print("\n================ QUESTION ================\n")
    print(question)

    route = router(question)

    print("\n================ SELECTED ROUTE ================\n")
    print(route)

    if route == "file":
        tool_output = file_search(question)

    elif route == "web":
        tool_output = web_search(question)

    else:
        tool_output = reasoning(question)

    print("\n================ TOOL OUTPUT ================\n")
    print(tool_output)

    final_answer = synthesize(question, tool_output, route)

    print("\n================ FINAL ANSWER ================\n")
    print(final_answer)

    return final_answer


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":

    q = input("Ask a question: ")
    run_agent(q)