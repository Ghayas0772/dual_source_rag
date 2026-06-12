import json
import os
from datetime import datetime
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# -----------------------------
# CONFIG
# -----------------------------
endpoint = "https://gghayas6346-2931-resource.services.ai.azure.com/api/projects/gghayas6346-2931"

client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
).get_openai_client()

# -----------------------------
# FILES
# -----------------------------
PROFILE_FILE = "profile.json"
MEMORY_FILE = "memory.json"

# -----------------------------
# INIT
# -----------------------------
def init():
    if not os.path.exists(PROFILE_FILE):
        json.dump({
            "name": None,
            "interests": [],
            "topics_count": {}
        }, open(PROFILE_FILE, "w"), indent=2)

    if not os.path.exists(MEMORY_FILE):
        json.dump([], open(MEMORY_FILE, "w"), indent=2)

# -----------------------------
# SAFE LLM CALL
# -----------------------------
def call(prompt):
    return client.responses.create(
        input=[{"role": "user", "content": prompt}],
        extra_body={
            "agent_reference": {
                "type": "agent_reference",
                "name": "dual-source-tutor-agent",
                "version": "12"
            }
        }
    ).output_text

# -----------------------------
# LOAD PROFILE
# -----------------------------
def load_profile():
    return json.load(open(PROFILE_FILE))

# -----------------------------
# UPDATE PROFILE AUTOMATICALLY
# -----------------------------
def update_profile(question):

    profile = load_profile()

    prompt = f"""
Extract user interests from this question.

Return JSON:
{{
  "interests": [],
  "main_topic": ""
}}

Question:
{question}
"""

    result = call(prompt)

    try:
        data = json.loads(result)
    except:
        return

    for i in data.get("interests", []):
        profile["interests"].append(i)

    topic = data.get("main_topic")

    if topic:
        profile["topics_count"][topic] = profile["topics_count"].get(topic, 0) + 1

    json.dump(profile, open(PROFILE_FILE, "w"), indent=2)

# -----------------------------
# STORE MEMORY
# -----------------------------
def store_memory(question, answer):

    memory = json.load(open(MEMORY_FILE))

    memory.append({
        "q": question,
        "a": answer,
        "time": datetime.now().isoformat()
    })

    # keep raw + summary balance
    memory = memory[-30:]

    json.dump(memory, open(MEMORY_FILE, "w"), indent=2)

# -----------------------------
# MEMORY SUMMARIZER
# -----------------------------
def summarize_memory():

    memory = json.load(open(MEMORY_FILE))

    if len(memory) < 5:
        return "No summary yet"

    prompt = f"""
Summarize these conversations:

{memory[-10:]}

Return 5 bullet insights only.
"""

    return call(prompt)

# -----------------------------
# SEMANTIC MEMORY SEARCH (SIMULATED)
# -----------------------------
def semantic_memory_search(question):

    memory = json.load(open(MEMORY_FILE))

    if not memory:
        return "No relevant memory"

    prompt = f"""
Find relevant past knowledge for this question:

Question:
{question}

Memory:
{memory[-10:]}

Return only most relevant past Q/A.
"""

    return call(prompt)

# -----------------------------
# BUILD CONTEXT (NEW MEMORY ENGINE)
# -----------------------------
def build_context(question):

    profile = load_profile()
    memory_summary = summarize_memory()
    relevant_memory = semantic_memory_search(question)

    return f"""
PROFILE:
{profile}

MEMORY SUMMARY:
{memory_summary}

RELEVANT MEMORY:
{relevant_memory}

QUESTION:
{question}
"""