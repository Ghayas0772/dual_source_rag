import streamlit as st
import json
import os
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from agent_production import run
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

LOG_DIR = "logs"

# -----------------------------
# LOAD LATEST TRACE
# -----------------------------
def load_latest_trace():
    files = sorted(os.listdir(LOG_DIR))
    if not files:
        return None

    with open(os.path.join(LOG_DIR, files[-1]), "r", encoding="utf-8") as f:
        return json.load(f)

# -----------------------------
# RUN SINGLE AGENT
# -----------------------------
def run_agent(question, version="12"):

    response = client.responses.create(
        input=[{"role": "user", "content": question}],
        extra_body={
            "agent_reference": {
                "name": agent_name,
                "version": version,
                "type": "agent_reference"
            }
        }
    )

    return response.output_text

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="AI Observability Dashboard", layout="wide")

st.title("🧠 AI Agent Observability Dashboard")

menu = st.sidebar.selectbox(
    "Select View",
    ["Run Agent", "A/B Comparison", "Trace Viewer"]
)

# -----------------------------
# RUN SINGLE AGENT
# -----------------------------
if menu == "Run Agent":

    st.subheader("Run Single Agent")

    question = st.text_input("Enter Question")

    version = st.selectbox("Agent Version", ["12", "13"])

    if st.button("Run"):

        answer = run_agent(question, version)

        st.markdown("### 🤖 Answer")
        st.write(answer)

# -----------------------------
# A/B COMPARISON
# -----------------------------
elif menu == "A/B Comparison":

    st.subheader("Compare Agent Versions (A vs B)")

    question = st.text_input("Enter Question")

    if st.button("Compare"):

        answer_a = run_agent(question, "12")
        answer_b = run_agent(question, "13")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("## 🅰 Agent A (v12)")
            st.write(answer_a)

        with col2:
            st.markdown("## 🅱 Agent B (v13)")
            st.write(answer_b)

# -----------------------------
# TRACE VIEWER
# -----------------------------
elif menu == "Trace Viewer":

    st.subheader("Trace Viewer")

    trace = load_latest_trace()

    if trace:

        st.json(trace)

        st.markdown("### Question")
        st.write(trace["question"])

        st.markdown("### Answer")
        st.write(trace["answer"])

        if "evaluation" in trace:
            st.markdown("### Evaluation")
            st.write(trace["evaluation"])

    else:
        st.warning("No traces found")