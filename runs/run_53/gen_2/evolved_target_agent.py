# Evo-mutated in gen 1
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
os.makedirs(WORKING_DIR, exist_ok=Tru