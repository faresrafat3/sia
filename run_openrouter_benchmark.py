"""
OpenRouter Benchmark Runner for GENESIS with Evolutionary Discovery.

Usage (after setting env):
export OPENAI_API_KEY="sk-or-your-openrouter-key"
export OPENAI_BASE_URL="https://openrouter.ai/api/v1"

python run_openrouter_benchmark.py --task spaceship-titanic --max_gen 3 --use_evolutionary_discovery

This will run the orchestrator with gpt-oss-120b:free for meta and task,
trigger the AlphaEvolve evolutionary engine if flag set,
and capture results for comparison against baseline (98.6% keyword matching).

See STRATEGIC_DEVELOPMENT_PLAN_2026_06.md Task for real run.

After run, check runs/run_*/ for:
- evolutionary_discovery.json (new evo metrics)
- evolved_target_agent.py (best variant)
- results.json, constitutional_report.json
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Run GENESIS benchmark on OpenRouter with gpt-oss-120b:free + evo")
    parser.add_argument("--task", type=str, default="spaceship-titanic", help="Bundled task")
    parser.add_argument("--max_gen", type=int, default=3)
    parser.add_argument("--run_id", type=int, default=1)
    parser.add_argument("--use_evolutionary_discovery", action="store_true", help="Enable AlphaEvolve engine")
    args = parser.parse_args()

    # Force OpenRouter + free model
    os.environ.setdefault("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: Set OPENAI_API_KEY to your OpenRouter key")
        sys.exit(1)

    cmd = [
        sys.executable, "-m", "genesis.orchestrator",
        "--task", args.task,
        "--max_gen", str(args.max_gen),
        "--run_id", str(args.run_id),
        "--backend", "openai",
        "--meta_model", "openai/gpt-oss-120b:free",
        "--task_model", "openai/gpt-oss-120b:free",
    ]
    if args.use_evolutionary_discovery:
        cmd.append("--use_evolutionary_discovery")

    print("Running GENESIS benchmark on OpenRouter...")
    print("Command:", " ".join(cmd))
    print("Model: openai/gpt-oss-120b:free (free tier)")
    print("This will exercise the new Evolutionary Discovery Engine (Task 6).")

    result = subprocess.run(cmd, check=False)

    if result.returncode == 0:
        print("\n✅ Run completed successfully!")
        print("Check runs/run_{}/ for results, evolutionary_discovery.json, evolved_target_agent.py".format(args.run_id))
        print("Compare to baseline 98.6% to see impact of legitimate thefts (AlphaEvolve + prior).")
    else:
        print("\n❌ Run failed with code", result.returncode)

if __name__ == "__main__":
    main()