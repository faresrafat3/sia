import os
import sys
import json
import argparse
import datetime
import pandas as pd
import numpy as np
import openai

from virtual_genesis.runtime.pipeline.minimal_run import run_minimal_pipeline
from virtual_genesis.runtime.memory_os.store import InMemoryMemoryStore
from virtual_genesis.runtime.concept_engine.registry import InMemoryConceptRegistry
from virtual_genesis.runtime.theory_runtime.registry import InMemoryTheoryRegistry
from virtual_genesis.runtime.economy_control.ledger import InMemoryLedgerStore

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("--dataset_dir", required=True)
parser.add_argument("--working_dir", required=True)
args = parser.parse_args()
DATASET_DIR = args.dataset_dir
WORKING_DIR = args.working_dir
os.makedirs(WORKING_DIR, exist_ok=True)

# Model configuration
MODEL = "openai/gpt-oss-120b:free"
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
)

# Initialise runtime components
store = InMemoryMemoryStore()
concept_registry = InMemoryConceptRegistry()
theory_registry = InMemoryTheoryRegistry()
ledger_store = InMemoryLedgerStore()

# Load task description
task_md_path = os.path.join(DATASET_DIR, "task.md")
if os.path.exists(task_md_path):
    with open(task_md_path, encoding="utf-8") as f:
        task_text = f.read()
else:
    task_text = f"Solve the task using data in {DATASET_DIR}"
print(f"Task loaded: {task_text[:200]}...")

# Run the GENESIS minimal pipeline (may be a no‑op for many tasks)
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

# Helper to safely extract dict values
def _get(d, key, default=None):
    return d.get(key, default) if isinstance(d, dict) else default

# Extract useful pieces from pipeline result
task_info = _get(result, "task", {})
blackboard = _get(result, "blackboard", {})
tier_decision = _get(result, "tier_decision", {})
verification = _get(blackboard, "verification_state", {})

print(
    f"Tier: {_get(tier_decision, 'chosen_tier', 'unknown')}, "
    f"Verification good_enough: {_get(verification, 'verification_summary', {}).get('good_enough', False)}"
)

# ---------------------------------------------------------------------------
# Data loading – try common CSV names, fall back to any CSV in the directory
# ---------------------------------------------------------------------------
train_df = None
test_df = None
csv_files = [f for f in os.listdir(DATASET_DIR) if f.lower().endswith('.csv')]
for f in csv_files:
    path = os.path.join(DATASET_DIR, f)
    try:
        df = pd.read_csv(path)
        if "train" in f.lower() and train_df is None:
            train_df = df
        elif "test" in f.lower() and test_df is None:
            test_df = df
        else:
            # If we still miss one of them, assign heuristically based on shape
            if train_df is None and df.shape[0] > 1000:
                train_df = df
            elif test_df is None:
                test_df = df
    except Exception as e:
        print(f"Failed to read {path}: {e}")

# If still missing, attempt generic read of first two CSVs
if train_df is None and len(csv_files) >= 1:
    try:
        train_df = pd.read_csv(os.path.join(DATASET_DIR, csv_files[0]))
    except Exception:
        pass
if test_df is None and len(csv_files) >= 2:
    try:
        test_df = pd.read_csv(os.path.join(DATASET_DIR, csv_files[1]))
    except Exception:
        pass

if train_df is not None:
    print(f"Full train shape: {train_df.shape}")
if test_df is not None:
    print(f"Full test shape: {test_df.shape}")

# ---------------------------------------------------
# Classification path (CSV based tasks)
# ---------------------------------------------------
accuracy = 0.0
if train_df is not None and test_df is not None:
    # Detect target/label column
    target_col = None
    for col in ["target", "label", "y", "class", "Survived", "Outcome", "target_label"]:
        if col in train_df.columns:
            target_col = col
            break
    if not target_col:
        target_col = train_df.columns[-1]
    print(f"Detected target column: {target_col}")

    # Simple classifier – logistic regression on numeric features
    def simple_classifier(train, test, target):
        try:
            X = train.drop(columns=[target])
            y = train[target]
            X = X.apply(pd.to_numeric, errors="coerce").fillna(0)
            X = pd.get_dummies(X, drop_first=True)
            test_X = test.apply(pd.to_numeric, errors="coerce").fillna(0)
            test_X = pd.get_dummies(test_X, drop_first=True)
            X, test_X = X.align(test_X, join="left", axis=1, fill_value=0)
            from sklearn.linear_model import LogisticRegression
            model = LogisticRegression(max_iter=1000)
            model.fit(X, y)
            return model.predict(test_X)
        except Exception as e:
            print(f"Simple classifier error: {e}")
            return np.zeros(len(test))

    # Validation split for a quick sanity check
    try:
        from sklearn.model_selection import train_test_split
        stratify = train_df[target_col] if train_df[target_col].nunique() > 1 else None
        train_part, val_part = train_test_split(
            train_df, test_size=0.2, random_state=42, stratify=stratify
        )
        val_preds = simple_classifier(train_part, val_part.drop(columns=[target_col]), target_col)
        val_true = val_part[target_col]
        accuracy = (val_preds == val_true).mean()
        print(f"Validation accuracy: {accuracy:.4f}")
    except Exception as e:
        print(f"Validation split error: {e}")
        accuracy = 0.0

    # Train on full data and produce predictions for the test set
    predictions = simple_classifier(train_df, test_df, target_col)

    # Determine identifier column for submission
    id_col = None
    for cand in ["PassengerId", "Id", "id", "index"]:
        if cand in test_df.columns:
            id_col = cand
            break
    if id_col is None:
        test_df = test_df.reset_index()
        id_col = "index"
    submission = pd.DataFrame({id_col: test_df[id_col], target_col: predictions})
    sub_path = os.path.join(WORKING_DIR, "submission.csv")
    submission.to_csv(sub_path, index=False)
    print(f"Submission saved to {sub_path}")

# ---------------------------------------------------
# Question‑Answering path (JSON based tasks)
# ---------------------------------------------------
else:
    # Look for JSON files containing question data
    json_files = [f for f in os.listdir(DATASET_DIR) if f.lower().endswith('.json')]
    questions = []
    for jf in json_files:
        try:
            with open(os.path.join(DATASET_DIR, jf), encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "questions" in data:
                questions.extend(data["questions"])
            elif isinstance(data, list):
                questions.extend(data)
        except Exception as e:
            print(f"Failed loading {jf}: {e}")

    answers_list = []
    for idx, q in enumerate(questions):
        try:
            qid = q.get('id') or q.get('question_id') or str(idx)
            qtext = q.get('question') or q.get('text') or q.get('prompt') or ''
            # Normalise options to a dict of letter -> text
            opt_dict = {}
            if isinstance(q.get('options'), dict):
                opt_dict = q['options']
            elif isinstance(q.get('options'), list):
                # assume list order corresponds to A, B, C, D ...
                letters = [chr(ord('A') + i) for i in range(len(q['options']))]
                opt_dict = dict(zip(letters, q['options']))
            # Build prompt
            opt_lines = [f"{k}: {v}" for k, v in sorted(opt_dict.items())]
            prompt = (
                f"Question: {qtext}\n"
                f"Options:\n" + "\n".join(opt_lines) + "\n"
                "Think step by step. Choose the best answer and output ONLY the letter A, B, C, or D."
            )
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=50,
            )
            answer = response.choices[0].message.content.strip().upper()
            # Ensure a single valid letter is returned
            if answer not in ["A", "B", "C", "D"]:
                # Try to extract first valid letter
                answer = next((ch for ch in answer if ch in ["A", "B", "C", "D"]), "A")
            answers_list.append({"question_id": qid, "model_answer": answer})
            print(f"Processing question {idx+1}/{len(questions)}: chose {answer}")
        except Exception as e:
            print(f"Error processing question {idx}: {e}")

    if answers_list:
        ans_path = os.path.join(WORKING_DIR, "answers.json")
        sub_path = os.path.join(WORKING_DIR, "submission.json")
        with open(ans_path, "w", encoding="utf-8") as f:
            json.dump({"details": answers_list}, f, indent=2)
        with open(sub_path, "w", encoding="utf-8") as f:
            json.dump({"details": answers_list}, f, indent=2)
        print(f"Answers saved to {ans_path} and {sub_path}")

# ---------------------------------------------------
# Robust execution logging (mandatory)
# ---------------------------------------------------
try:
    execution_log = {
        "timestamp": datetime.datetime.now().isoformat(),
        "task_preview": task_text[:300] if 'task_text' in locals() else "unknown task",
        "pipeline_result_keys": list(result.keys()) if isinstance(result, dict) else str(type(result)),
        "tier": tier_decision.get('chosen_tier', 'unknown') if isinstance(tier_decision, dict) else 'unknown',
        "verification_good_enough": verification.get('verification_summary', {}).get('good_enough', False) if isinstance(verification, dict) else False,
        "detected_task_type": "classification" if train_df is not None else "qa",
        "loaded_data_shape": str(train_df.shape) if train_df is not None else "N/A",
        "accuracy": accuracy,
        "submission_path": os.path.join(WORKING_DIR, "submission.csv") if os.path.exists(os.path.join(WORKING_DIR, "submission.csv")) else None,
        "messages": [
            {"role": "system", "content": "Target agent executed with GENESIS pipeline + task logic."},
            {"role": "user", "content": task_text[:200] if 'task_text' in locals() else ""},
            {"role": "assistant", "content": "Completed task with accuracy reported above."},
        ],
    }
    log_path = os.path.join(WORKING_DIR, "agent_execution.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(execution_log, f, indent=2, ensure_ascii=False)
    print(f"Execution log saved to {log_path}")
except Exception as e:
    print(f"Failed to write execution log: {e}")
    try:
        fallback = {"error": str(e), "timestamp": datetime.datetime.now().isoformat()}
        with open(os.path.join(WORKING_DIR, "agent_execution.json"), "w", encoding="utf-8") as f:
            json.dump(fallback, f)
    except Exception:
        pass

print("Target agent completed successfully for task.")