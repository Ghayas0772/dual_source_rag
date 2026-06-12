import streamlit as st
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from openai import AzureOpenAI

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
# UI
# -----------------------------
st.title("🧠 RAG Debug Dashboard (Your Agent)")

question = st.text_input("Ask your question")

if st.button("Run Agent") and question:

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

    # -------------------------
    # FINAL ANSWER
    # -------------------------
    st.subheader("🟢 Final Answer")
    st.write(response.output_text)

    data = response.model_dump()

    # -------------------------
    # TRACE SECTION
    # -------------------------
    st.subheader("🔍 Execution Trace")

    output = data.get("output", [])

    file_used = False

    for item in output:

        # -------------------------
        # FILE SEARCH STEP
        # -------------------------
        if item.get("type") == "file_search_call":
            file_used = True
            st.markdown("### 📂 File Search Triggered")
            st.write("Query:", item.get("queries"))
            st.write("Vector Store:", item.get("vector_store_ids"))

        # -------------------------
        # MESSAGE STEP (FIXED INDENTATION)
        # -------------------------
        if item.get("type") == "message":
            st.markdown("### 🤖 Model Output")

            for c in item.get("content", []):
                text = c.get("text", "")
                st.write(text)

                annotations = c.get("annotations", [])

                if annotations:
                    st.markdown("### 📌 Retrieved Chunks (Vector Search Output)")

                    for idx, a in enumerate(annotations):

                        file_name = a.get("filename")
                        file_id = a.get("file_id")
                        index = a.get("index")

                        st.markdown(f"#### Chunk {idx+1}")

                        st.write("📄 File:", file_name)
                        st.write("🆔 File ID:", file_id)
                        st.write("📍 Index:", index)

                        st.code(str(a), language="json")

    # -------------------------
    # RAG DETECTION
    # -------------------------
    st.subheader("🧠 RAG Detection")

    if file_used:
        st.success("File Search WAS used (RAG active)")
    else:
        st.warning("No File Search detected (likely GPT-only)")