import json
import os
from datetime import datetime
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
# LOG DIRECTORY
# -----------------------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# -----------------------------
# SAVE TRACE
# -----------------------------
def save_trace(data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"{LOG_DIR}/trace_{timestamp}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"\n📁 Trace saved to: {file_path}")

# -----------------------------
# EVALUATION AGENT
# -----------------------------
def evaluate_answer(question, answer):

    prompt = f"""
You are an AI evaluator.

Evaluate the answer below.

Question:
{question}

Answer:
{answer}

Return JSON:
{{
  "correctness_score": 0-10,
  "grounding_score": 0-10,
  "hallucination_risk": "low | medium | high",
  "clarity_score": 0-10,
  "overall_score": 0-10,
  "feedback": "short explanation"
}}
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
# RUN AGENT + EVALUATION
# -----------------------------
def run_agent(question):

    print("\n================ RUNNING AGENT =================\n")

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
    data = response.model_dump()

    # -----------------------------
    # PRINT ANSWER
    # -----------------------------
    print("\n================ ANSWER =================\n")
    print(answer)

    # -----------------------------
    # EVALUATION STEP
    # -----------------------------
    print("\n================ EVALUATION =================\n")
    evaluation = evaluate_answer(question, answer)
    print(evaluation)

    # -----------------------------
    # TRACE RECORD
    # -----------------------------
    trace_record = {
        "question": question,
        "answer": answer,
        "evaluation": evaluation,
        "model": data.get("model"),
        "timestamp": datetime.now().isoformat(),
        "output": data.get("output", []),
        "usage": data.get("usage", {})
    }

    # -----------------------------
    # SAVE TRACE
    # -----------------------------
    save_trace(trace_record)

    return trace_record

# -----------------------------
# REPLAY LAST TRACE
# -----------------------------
def load_last_trace():

    files = sorted(os.listdir(LOG_DIR))

    if not files:
        print("No traces found.")
        return None

    latest = files[-1]
    path = os.path.join(LOG_DIR, latest)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("\n================ REPLAY TRACE =================\n")
    print("Question:", data["question"])
    print("Answer:", data["answer"])
    print("\nEvaluation:", data.get("evaluation"))

    return data

def compare_agents(question):

    print("\n================ RUNNING AGENT A =================\n")

    # -------------------------
    # AGENT A (current version)
    # -------------------------
    response_a = client.responses.create(
        input=[{"role": "user", "content": question}],
        extra_body={
            "agent_reference": {
                "name": agent_name,
                "version": "12",
                "type": "agent_reference"
            }
        }
    )

    answer_a = response_a.output_text

    # -------------------------
    # AGENT B (simulated upgraded version)
    # -------------------------
    print("\n================ RUNNING AGENT B =================\n")

    response_b = client.responses.create(
        input=[{"role": "user", "content": question}],
        extra_body={
            "agent_reference": {
                "name": agent_name,
                "version": "13",
                "type": "agent_reference"
            }
        }
    )

    answer_b = response_b.output_text

    # -------------------------
    # EVALUATE BOTH
    # -------------------------
    print("\n================ EVALUATING A =================\n")
    eval_a = evaluate_answer(question, answer_a)

    print("\n================ EVALUATING B =================\n")
    eval_b = evaluate_answer(question, answer_b)

    print("A Evaluation:", eval_a)
    print("B Evaluation:", eval_b)

    # -------------------------
    # SIMPLE COMPARISON LOGIC
    # -------------------------
    def extract_score(eval_text):
        try:
            data = json.loads(eval_text)
            return data.get("overall_score", 0)
        except:
            return 0

    score_a = extract_score(eval_a)
    score_b = extract_score(eval_b)

    # -------------------------
    # PICK BEST
    # -------------------------
    if score_b > score_a:
        best = "B"
        best_answer = answer_b
    else:
        best = "A"
        best_answer = answer_a

    # -------------------------
    # FINAL OUTPUT
    # -------------------------
    print("\n================ WINNER =================\n")
    print("Best Agent:", best)
    print(best_answer)

    # -------------------------
    # SAVE OPTIMIZATION TRACE
    # -------------------------
    trace = {
        "question": question,
        "agent_a_answer": answer_a,
        "agent_b_answer": answer_b,
        "evaluation_a": eval_a,
        "evaluation_b": eval_b,
        "winner": best,
        "winner_answer": best_answer,
        "timestamp": datetime.now().isoformat()
    }

    save_trace(trace)

    return trace
# -----------------------------
# MAIN MENU
# -----------------------------
if __name__ == "__main__":

    print("\n1. Run Single Agent")
    print("2. Replay Last Trace")
    print("3. Compare Agent Versions (A/B Test)")

    choice = input("\nSelect option: ")

    if choice == "1":
        q = input("Ask a question: ")
        run_agent(q)

    elif choice == "2":
        load_last_trace()

    elif choice == "3":
        q = input("Ask a question: ")
        compare_agents(q)

    else:
        print("Invalid option")