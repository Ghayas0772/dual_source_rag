#COMPLETE “PLAYGROUND-STYLE TRACE” APP.PY

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
import json

# ----------------------------
# CONFIG
# ----------------------------
endpoint = "https://gghayas6346-2931-resource.services.ai.azure.com/api/projects/gghayas6346-2931"

project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

openai_client = project_client.get_openai_client()

agent_name = "dual-source-tutor-agent"
agent_version = "12"

# ----------------------------
# USER INPUT
# ----------------------------
question = input("Ask a question: ")

# ----------------------------
# CALL AGENT
# ----------------------------
response = openai_client.responses.create(
    input=[{"role": "user", "content": question}],
    extra_body={
        "agent_reference": {
            "name": agent_name,
            "version": agent_version,
            "type": "agent_reference"
        }
    }
)

# ----------------------------
# OUTPUT TEXT
# ----------------------------
print("\n================ FINAL ANSWER ================\n")
print(response.output_text)

# ----------------------------
# TRACE EXTRACTION (PLAYGROUND STYLE)
# ----------------------------
print("\n================ STEP TRACE ================\n")

data = response.model_dump()

output = data.get("output", [])

step_num = 1

for item in output:

    # STEP 1: File Search
    if item.get("type") == "file_search_call":
        print(f"STEP {step_num}: File Search Triggered")
        print("→ Query:", item.get("queries"))
        print("→ Vector Stores:", item.get("vector_store_ids"))
        step_num += 1

    # STEP 2: Message / Answer
    elif item.get("type") == "message":
        print(f"\nSTEP {step_num}: LLM Response Generated")

        content = item.get("content", [])
        for c in content:
            text = c.get("text", "")

            # detect citations (your RAG proof)
            annotations = c.get("annotations", [])
            if annotations:
                print("→ Source Used:")
                for a in annotations:
                    print("   - File:", a.get("filename"))

            print("\n→ Response Preview:\n", text[:500])
        step_num += 1

# ----------------------------
# TOOL SUMMARY
# ----------------------------
print("\n================ TOOL SUMMARY ================\n")

tools = data.get("tools", [])

for t in tools:
    print("Tool:", t.get("type"))