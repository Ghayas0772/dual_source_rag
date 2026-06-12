import streamlit as st
import json
import os
from agent_production import run

# -----------------------------
# UI CONFIG
# -----------------------------
st.set_page_config(page_title="AI Agent Dashboard", layout="wide")

st.title("🧠 AI Agent Observability Dashboard")

# -----------------------------
# INPUT SECTION
# -----------------------------
question = st.text_input("Ask your agent question")

if st.button("Run Agent") and question:

    with st.spinner("Running agent..."):
        result = run(question)

    st.success("Done!")

# -----------------------------
# TRACE VIEWER
# -----------------------------
st.subheader("📊 Latest Trace Files")

trace_files = sorted([f for f in os.listdir() if f.startswith("trace_")])

if trace_files:
    latest = trace_files[-1]

    with open(latest, "r") as f:
        trace_data = json.load(f)

    st.write("Latest Trace File:", latest)

    st.json(trace_data)
else:
    st.warning("No trace files found")

# -----------------------------
# MEMORY VIEWER
# -----------------------------
st.subheader("🧠 Memory Store")

if os.path.exists("memory.json"):
    with open("memory.json", "r") as f:
        memory = json.load(f)

    st.json(memory)
else:
    st.warning("No memory found")