"""
Test for AlphaEvolve-style Evolutionary Discovery Engine.

Ties directly to:
- GENESIS_DeepMind_AlphaEvolve_FunSearch_Theft_AR.md (Task 6)
- Self-improvement / Bridge task
- Uses GENESIS harness (pipeline, eval, constitutional) as evaluator.

High-quality skeleton tests: basic functionality, integration with existing artifacts,
and that it produces diverse population + lineage.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

# Import the function from the orchestrator (it's defined there for now; later can move to genesis/evo/)
from genesis.orchestrator import evolutionary_discovery_engine


def test_evolutionary_discovery_basic():
    """Basic smoke test: runs, produces population, best variant, lineage."""
    sample_code = """
def target_agent(dataset_dir, working_dir):
    # Simple baseline agent
    import pandas as pd
    # ... (mock)
    return {"success": True, "score": 0.8}
"""
    task_text = "Solve the spaceship-titanic classification task using the GENESIS pipeline."

    result = evolutionary_discovery_engine(
        current_agent_code=sample_code,
        task_text=task_text,
        population_size=4,
        generations=1,
    )

    assert "best_variant" in result
    assert "population" in result
    assert len(result["population"]) == 4
    assert "lineage" in result
    assert result["metrics"]["best_fitness"] > 0
    assert "parent" in result["best_variant"]
    assert result["best_variant"]["fitness"] >= 0.1


def test_evolutionary_discovery_with_diversity_and_lineage():
    """Ensure diversity and lineage tracking work as per theft memo (population diversity + lineage)."""
    sample_code = "def foo(): pass  # baseline"

    result = evolutionary_discovery_engine(
        current_agent_code=sample_code,
        task_text="Test task",
        population_size=6,
        generations=2,
        diversity_weight=0.4,
    )

    parents = [p["parent"] for p in result["population"]]
    unique_parents = set(parents)
    assert len(unique_parents) >= 2, "Should have some diversity in parents (lineage)"

    # Check lineage has entries
    assert len(result["lineage"]) >= 6

    # Final scores should be computed
    for p in result["population"]:
        assert "final_score" in p or "score" in p


def test_evolutionary_discovery_uses_harness_proxy():
    """Test that the evaluator prefers real GENESIS artifacts when present (ties to existing eval/constitutional)."""
    # Create a fake results.json to simulate real eval data from run_evaluation
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        os.makedirs("runs/run_1/gen_1", exist_ok=True)
        fake_results = {"overall_score": 0.92, "success_rate": 0.91}
        with open("runs/run_1/gen_1/results.json", "w") as f:
            json.dump(fake_results, f)

        sample_code = "def improved(): pass"

        result = evolutionary_discovery_engine(
            current_agent_code=sample_code,
            task_text="Test",
            population_size=3,
            generations=1,
        )

        # The best should have picked up the high score from the fake results
        best_fitness = result["best_variant"]["fitness"]
        assert best_fitness > 0.8, "Should have used the harness results.json proxy for higher fitness"


def test_evolutionary_discovery_skeleton_note():
    """Ensure the note reminds that this is skeleton and full version uses LLM + real pipeline."""
    result = evolutionary_discovery_engine(
        current_agent_code="def x(): pass",
        task_text="dummy",
        population_size=2,
    )
    assert "Skeleton implementation from AlphaEvolve theft" in result["note"]
    assert "LLM for true mutation/crossover" in result["note"]
    assert "GRASP gating" in result["note"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])