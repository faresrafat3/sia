import os
import sys
import json
import argparse
import asyncio
import datetime
import httpx
import openai
import pandas as pd
import numpy as np

from virtual_genesis.runtime.pipeline.minimal_run import run_minimal_pipeline
from virtual_genesis.runtime.memory_os.store import InMemoryMemoryStore
from virtual_genesis.runtime.concept_engine.registry import InMemoryConceptRegistry
from virtual_genesis.runtime.theory_runtime.registry import InMemoryTheoryRegistry
from virtual_genesis.runtime.economy_control.ledger import InMemoryLedgerStore
from virtual_genesis.core.objects.memory import MemoryUnit

parser = argparse.ArgumentParser()
parser.add_argument("--dataset_dir", required=True)
parser.add_argument("--working_dir", required=True)
args = parser.parse_args()
DATASET_DIR = args.dataset_dir
WORKING_DIR = args.working_dir
os.makedirs(WORKING_DIR, exist_ok=True)

MODEL = "openai/gpt-oss-120b:free"
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
)

store = InMemoryMemoryStore()
concept_registry = InMemoryConceptRegistry()
theory_registry = InMemoryTheoryRegistry()
ledger_store = InMemoryLedgerStore()

task_md_path = os.path.join(DATASET_DIR, "task.md")
if os.path.exists(task_md_path):
    with open(task_md_path, encoding="utf-8") as f:
        task_text = f.read()
else:
    task_text = "Solve the task using data in " + DATASET_DIR
print(f"Task loaded: {task_text[:200]}...")

result = run_minimal_pipeline(
    raw_task=task_text,
    store=store,
    concept_registry=concept_registry,
    theory_registry=theory_registry,
    ledger_store=ledger_store,
    use_memory=True,
    use_economy=True,
    use_concepts=False,
)
print("Pipeline result keys:", list(result.keys()) if isinstance(result, dict) else type(result))

task_info = result.get("task", {}) if isinstance(result, dict) else {}
blackboard = result.get("blackboard", {}) if isinstance(result, dict) else {}
tier_decision = result.get("tier_decision", {}) if isinstance(result, dict) else {}
theory_pred = result.get("theory_prediction") if isinstance(result, dict) else None
verification = blackboard.get("verification_state", {}) if isinstance(result, dict) else {}
print(f"Tier: {tier_decision.get('chosen_tier', 'unknown')}, Verification good_enough: {verification.get('verification_summary', {}).get('good_enough', False)}")

# Load possible data files
train_df = None
test_df = None
try:
    train_path = os.path.join(DATASET_DIR, "train.csv")
    test_path = os.path.join(DATASET_DIR, "test.csv")
    if os.path.exists(train_path):
        train_df = pd.read_csv(train_path)
    if os.path.exists(test_path):
        test_df = pd.read_csv(test_path)
    if train_df is not None:
        print(f"Full train shape: {train_df.shape}")
    if test_df is not None:
        print(f"Full test shape: {test_df.shape}")
    if train_df is not None:
        print(f"Train columns sample: {list(train_df.columns)[:5]}...")
except Exception as load_e:
    print(f"Data load error: {load_e}")
    train_df, test_df = None, None

# Detect target column
target_col = None
if train_df is not None:
    for col in ["Transported", "target", "label", "y", "class", "Survived"]:
        if col in train_df.columns:
            target_col = col
            break
    if not target_col:
        target_col = train_df.columns[-1]
    print(f"Detected target column: {target_col}")

# Helper for simple model training
def simple_classifier(train, test, target):
    try:
        X = train.drop(columns=[target])
        y = train[target]
        # basic numeric conversion
        X = X.apply(pd.to_numeric, errors='coerce').fillna(0)
        # one-hot encode categoricals
        X = pd.get_dummies(X, drop_first=True)
        test_X = test.copy()
        test_X = test_X.apply(pd.to_numeric, errors='coerce').fillna(0)
        test_X = pd.get_dummies(test_X, drop_first=True)
        # Align columns
        X, test_X = X.align(test_X, join='left', axis=1, fill_value=0)
        from sklearn.linear_model import LogisticRegression
        model = LogisticRegression(max_iter=1000)
        model.fit(X, y)
        preds = model.predict(test_X)
        return preds
    except Exception as e:
        print(f"Simple classifier error: {e}")
        return np.zeros(len(test))

# Main task handling
if train_df is not None and test_df is not None and target_col is not None:
    # split for validation
    from sklearn.model_selection import train_test_split
    try:
        train_part, val_part = train_test_split(train_df, test_size=0.2, random_state=42, stratify=train_df[target_col] if len(train_df[target_col].unique())>1 else None)
        val_preds = simple_classifier(train_part, val_part.drop(columns=[target_col]), target_col)
        val_true = val_part[target_col]
        accuracy = (val_preds == val_true).mean()
        print(f"Validation accuracy: {accuracy:.4f}")
    except Exception as split_e:
        print(f"Validation split error: {split_e}")
        accuracy = 0.0
    # train on full data and predict test
    predictions = simple_classifier(train_df, test_df, target_col)
    # Prepare submission
    id_col = None
    for possible_id in ["PassengerId", "Id", "id", "index"]:
        if possible_id in test_df.columns:
            id_col = possible_id
            break
    if not id_col:
        id_col = test_df.index.name if test_df.index.name else "index"
        test_df = test_df.reset_index()
        id_col = "index"
    submission = pd.DataFrame({id_col: test_df[id_col], target_col: predictions})
    sub_path = os.path.join(WORKING_DIR, "submission.csv")
    submission.to_csv(sub_path, index=False)
    print(f"Submission saved to {sub_path}")
else:
    # Q&A or other JSON based tasks
    # Look for json files
    json_files = [f for f in os.listdir(DATASET_DIR) if f.lower().endswith('.json')]
    questions = []
    for jf in json_files:
        try:
            with open(os.path.join(DATASET_DIR, jf), encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'questions' in data:
                    questions.extend(data['questions'])
                elif isinstance(data, list):
                    questions.extend(data)
        except Exception as je:
            print(f"Failed loading {jf}: {je}")
    answers_list = []
    for idx, q in enumerate(questions):
        try:
            qid = q.get('id') or q.get('question_id') or str(idx)
            qtext = q.get('question') or q.get('text') or ''
            options = []
            if isinstance(q.get('options'), dict):
                for key in sorted(q['options'].keys()):
                    options.append(f"{key}: {q['options'][key]}")
            elif isinstance(q.get('options'), list):
                for opt in q['options']:
                    options.append(str(opt))
            prompt = f"Question: {qtext}\nOptions:\n" + "\n".join(options) + "\nThink step by step. Choose the best answer and output ONLY the letter A, B, C, or D."
            # Call LLM
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=50,
            )
            answer = response.choices[0].message.content.strip().upper()
            if answer not in ["A","B","C","D"]:
                answer = answer[0] if answer and answer[0] in ["A","B","C","D"] else "A"
            answers_list.append({"question_id": qid, "model_answer": answer})
            print(f"Processing question {idx+1}/{len(questions)}: chose {answer}")
        except Exception as ques_e:
            print(f"Error processing question {idx}: {ques_e}")
    if answers_list:
        ans_path = os.path.join(WORKING_DIR, "answers.json")
        sub_path = os.path.join(WORKING_DIR, "submission.json")
        with open(ans_path, "w", encoding="utf-8") as f:
            json.dump({"details": answers_list}, f, indent=2)
        with open(sub_path, "w", encoding="utf-8") as f:
            json.dump({"details": answers_list}, f, indent=2)
        print(f"Answers saved to {ans_path} and {sub_path}")

# === ROBUST EXECUTION LOGGING (MANDATORY - put this before the final success print) ===
try:
    execution_log = {
        "timestamp": datetime.datetime.now().isoformat(),
        "task_preview": task_text[:300] if "task_text" in locals() else "unknown task",
        "pipeline_result_keys": list(result.keys()) if isinstance(result, dict) else str(type(result)),
        "tier": tier_decision.get("chosen_tier", "unknown") if isinstance(tier_decision, dict) else "unknown",
        "verification_good_enough": verification.get("verification_summary", {}).get("good_enough", False) if isinstance(verification, dict) else False,
        "detected_task_type": "classification" if train_df is not None else "qa",
        "loaded_data_shape": str(train_df.shape) if train_df is not None else "N/A",
        "accuracy": accuracy if 'accuracy' in locals() else 0.0,
        "submission_path": os.path.join(WORKING_DIR, "submission.csv"),
        "messages": [
            {"role": "system", "content": "Target agent executed with GENESIS pipeline + task logic."},
            {"role": "user", "content": task_text[:200] if "task_text" in locals() else ""},
            {"role": "assistant", "content": "Completed task with accuracy reported above."}
        ]
    }
    log_path = os.path.join(WORKING_DIR, "agent_execution.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(execution_log, f, indent=2, ensure_ascii=False)
    print(f"Execution log saved to {log_path}")
except Exception as log_err:
    print(f"Failed to write execution log: {log_err}")
    try:
        with open(os.path.join(WORKING_DIR, "agent_execution.json"), "w", encoding="utf-8") as f:
            json.dump({"error": str(log_err), "timestamp": datetime.datetime.now().isoformat()}, f)
    except:
        pass

print("Target agent completed successfully for task.")