import streamlit as st
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

openai_client = project_client.get_openai_client()

agent_name = "dual-source-tutor-agent"
agent_version = "12"

# -----------------------------
# UI CONFIG
# -----------------------------
st.set_page_config(layout="wide")

st.title("🧠 AI Playground Clone (Your Agent)")

# -----------------------------
# SESSION STATE (chat history)
# -----------------------------
if "chat" not in st.session_state:
    st.session_state.chat = []

# -----------------------------
# LAYOUT
# -----------------------------
col1, col2 = st.columns([2, 1])

# -----------------------------
# CHAT PANEL
# -----------------------------
with col1:

    st.subheader("💬 Chat")

    user_input = st.text_input("Ask something")

    if st.button("Send") and user_input:

        response = openai_client.responses.create(
            input=[{"role": "user", "content": user_input}],
            extra_body={
                "agent_reference": {
                    "name": agent_name,
                    "version": agent_version,
                    "type": "agent_reference"
                }
            }
        )

        data = response.model_dump()
        output = data.get("output", [])

        # store chat
        st.session_state.chat.append({
            "user": user_input,
            "ai": response.output_text,
            "trace": output
        })

    # show chat history
    for chat in st.session_state.chat[::-1]:

        st.markdown("### 🧑 You")
        st.write(chat["user"])

        st.markdown("### 🤖 AI")
        st.write(chat["ai"])

# -----------------------------
# TRACE PANEL
# -----------------------------
with col2:

    st.subheader("🔍 Trace Explorer")

    if st.session_state.chat:

        last_trace = st.session_state.chat[-1]["trace"]

        file_used = False

        for item in last_trace:

            # FILE SEARCH
            if item.get("type") == "file_search_call":
                file_used = True
                st.markdown("### 📂 File Search")
                st.write("Query:", item.get("queries"))

            # MESSAGE + CHUNKS
            if item.get("type") == "message":
                st.markdown("### 🤖 Model Output")

                for c in item.get("content", []):

                    st.write(c.get("text", ""))

                    annotations = c.get("annotations", [])

                    if annotations:
                        st.markdown("### 📌 Retrieved Chunks")

                        for idx, a in enumerate(annotations):

                            st.markdown(f"#### Chunk {idx+1}")
                            st.write("File:", a.get("filename"))
                            st.code(str(a), language="json")

        # RAG status
        st.subheader("🧠 RAG Status")

        if file_used:
            st.success("RAG ACTIVE (File Search used)")
        else:
            st.warning("No RAG detected")