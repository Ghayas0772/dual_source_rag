import json
import os
from datetime import datetime
from vector_memory import add_memory, build_context

# -----------------------------
# FILE PATHS
# -----------------------------
PROFILE_FILE = "user_profile.json"
MEMORY_FILE = "conversation_memory.json"

# -----------------------------
# INIT FILES IF NOT EXIST
# -----------------------------
def init():
    if not os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "w") as f:
            json.dump({
                "name": None,
                "interests": [],
                "skill_level": "beginner"
            }, f, indent=2)

    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            json.dump([], f, indent=2)

# -----------------------------
# LOAD PROFILE
# -----------------------------
def load_profile():
    with open(PROFILE_FILE, "r") as f:
        return json.load(f)

# -----------------------------
# UPDATE PROFILE
# -----------------------------
def update_profile(key, value):
    profile = load_profile()
    profile[key] = value

    with open(PROFILE_FILE, "w") as f:
        json.dump(profile, f, indent=2)

# -----------------------------
# ADD MEMORY
# -----------------------------
def add_memory(question, answer):

    with open(MEMORY_FILE, "r") as f:
        memory = json.load(f)

    memory.append({
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer
    })

    # keep last 20 only
    memory = memory[-20:]

    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

# -----------------------------
# LOAD MEMORY SUMMARY
# -----------------------------
def get_memory_summary():

    with open(MEMORY_FILE, "r") as f:
        memory = json.load(f)

    if not memory:
        return "No previous conversations."

    summary = []
    for m in memory[-5:]:
        summary.append(f"Q: {m['question']} | A: {m['answer'][:80]}")

    return "\n".join(summary)

# -----------------------------
# BUILD CONTEXT FOR AGENT
# -----------------------------
def build_context(question):

    profile = load_profile()
    memory = get_memory_summary()

    context = f"""
USER PROFILE:
Name: {profile.get('name')}
Interests: {profile.get('interests')}
Skill Level: {profile.get('skill_level')}

RECENT MEMORY:
{memory}

CURRENT QUESTION:
{question}
"""
    return context