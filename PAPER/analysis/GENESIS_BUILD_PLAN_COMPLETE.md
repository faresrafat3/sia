# GENESIS — خطة البناء الكاملة التنفيذية
# تاريخ: 2026-06-08
# بناءً على: Theft Audit + Full Inventory + Architecture Plan

---

## المبدأ الحاكم لكل شيء

```
كل مكوّن = Section واضحة في genesis/
كل Section = لها:
  1. مجلد خاص (genesis/skill_engine/ مش ملف واحد)
  2. __init__.py يُصدّر الواجهة العامة فقط
  3. tests/test_{section}.py
  4. orchestrator يستدعيها بـ import نظيف
  5. artifacts واضحة الـ schema

الـ agent (target_agent.py) يستدعي tools من:
  from genesis.tool_hub import get_tool, web_search, skill_use
وليس:
  from genesis.tools.web_search import web_search  ← (القديم)
```

---

## البنية الجديدة الكاملة لـ genesis/

```
genesis/
│
├── orchestrator.py          ← بدون تغيير جوهري (يضيف imports فقط)
├── util.py                  ← بدون تغيير
├── llm_helpers.py           ← بدون تغيير
│
│─── SECTION A: TOOL HUB ──────────────────────────────────────────
├── tool_hub/
│   ├── __init__.py          ← exports: get_tool(), invoke(), catalog()
│   ├── registry.py          ← ToolRegistry, ToolSpec
│   ├── executor.py          ← safe_invoke(), sandbox_run()
│   └── tools/
│       ├── web_search.py    ← wraps genesis/tools/web_search.py
│       ├── code_exec.py     ← sandbox execution
│       ├── file_ops.py      ← read/write files
│       ├── llm_call.py      ← wraps api_key_pool + util.py
│       └── skill_use.py     ← calls skill_engine.execute()
│
│─── SECTION B: SKILL ENGINE ──────────────────────────────────────
├── skill_engine/
│   ├── __init__.py          ← exports: register(), retrieve(), execute(), evolve()
│   ├── skill.py             ← Skill, SkillContract(P,O,A,V,F), SkillFolder
│   ├── library.py           ← SkillLibrary (SQLite + filesystem)
│   ├── extractor.py         ← extract_from_agent() (MUSE pattern)
│   ├── evaluator.py         ← run_tests() sandbox (MUSE create→eval→register)
│   ├── graph.py             ← SkillGraph HSEG (SkillOps dep/comp/red/alt)
│   ├── retriever.py         ← hybrid BM25+semantic (SkillOps formula)
│   ├── evolver.py           ← EvoSkill 3-agent loop
│   └── skills/              ← skill packages (filesystem)
│       ├── catalog.yaml     ← auto-generated, injected in system prompt
│       ├── web_search_arabic/
│       │   ├── SKILL.md
│       │   ├── scripts/search.py
│       │   ├── tests/test_search.py
│       │   └── .memory.md
│       └── ...
│
│─── SECTION C: META ENGINE ───────────────────────────────────────
├── meta_engine/
│   ├── __init__.py          ← exports: analyze(), gradient(), synthesize()
│   ├── trajectory.py        ← GenerationTrajectory, GenerationPoint
│   ├── textgrad.py          ← TextVariable, TGD, TextLoss (TextGrad API)
│   ├── proposer.py          ← ProposerAgent (EvoSkill Proposer)
│   └── optimizer.py         ← MetaOptimizer (runs trajectory→gradient→update)
│
│─── SECTION D: AGENT HUB ─────────────────────────────────────────
├── agent_hub/
│   ├── __init__.py          ← exports: create_agent(), load_agent(), AgentSpec
│   ├── agent.py             ← AgentSpec (Soul+Memory+Tools+Skills+BDI)
│   ├── registry.py          ← AgentRegistry (CRUD + REST foundation)
│   ├── soul/
│   │   ├── soul.py          ← AgentSoul dataclass
│   │   └── souls/           ← soul.md files per agent type
│   │       ├── research_agent.soul.md
│   │       └── default.soul.md
│   └── memory/
│       ├── manager.py       ← AgentMemoryManager
│       ├── working.py       ← WorkingMemory (context window)
│       ├── episodic.py      ← EpisodicMemory (timestamped)
│       ├── semantic.py      ← SemanticMemory (facts)
│       └── procedural.py    ← ProceduralMemory → SkillEngine bridge
│
│─── SECTION E: SAFETY ENGINE ─────────────────────────────────────
├── safety_engine/
│   ├── __init__.py          ← exports: check_budget(), check_halt()
│   ├── budget.py            ← BudgetGuard (cost+time+calls)
│   ├── hallucination.py     ← HallucinationGuard (rate threshold)
│   └── escalation.py       ← EscalationPolicy (warn→pause→halt)
│
│─── SECTION F: TELEMETRY ENGINE ──────────────────────────────────
├── telemetry/
│   ├── __init__.py          ← exports: log_event(), get_run_summary()
│   ├── telemetry.py         ← RunTelemetry, TelemetryEvent
│   └── reporter.py          ← run_summary.json generator
│
│─── EXISTING (لا تتغير) ──────────────────────────────────────────
├── tools/                   ← يُبقى (legacy + web_search أصله هنا)
│   └── web_search.py        ← ToolHub يُغلّفها (لا يحذفها)
├── goal_specification.py    ← يُنقل تدريجياً لـ INTENT ENGINE
├── open_task_evaluator.py   ← يُبقى
├── constitutional_evaluator.py ← يُبقى
├── context_manager.py       ← يُبقى
├── enhanced_pipeline_bridge.py ← يُبقى
├── research_memory.py       ← يُبقى
├── spin_feedback.py         ← يُبقى
└── cognitive_bridge.py      ← يُبقى
```

---

## الخطة التنفيذية — بالتفاصيل الكاملة

---

### PHASE 1: TOOL HUB (أسبوع 1)

**الهدف:** tools مش مدمجة في agents — الـ agent يستدعيها من hub

#### الملفات المبنية

**genesis/tool_hub/registry.py**
```python
# مسروق من: MCP Tool Specification
@dataclass
class ToolSpec:
    name: str
    description: str          # للـ catalog (minimal tokens)
    version: str
    input_schema: dict        # JSON Schema
    output_schema: dict       # JSON Schema
    preconditions: list[str]  # SkillOps-inspired
    failure_modes: list[str]
    cost_per_call_usd: float
    requires_sandbox: bool
    executor: callable

class ToolRegistry:
    def register(tool: ToolSpec)
    def get(name: str) → ToolSpec
    def catalog() → str          # YAML للـ system prompt (name+desc فقط)
    def invoke(name, args) → ToolResult
    def discover() → list[ToolSpec]  # MCP-style
```

**genesis/tool_hub/tools/web_search.py**
```python
# يُغلّف genesis/tools/web_search.py
# لا يكسر الكود القديم — backward compatible
WEB_SEARCH_TOOL = ToolSpec(
    name="web_search",
    description="Search web for real-time information",
    executor=lambda args: web_search(**args),  # wraps existing function
    ...
)
```

**genesis/tool_hub/executor.py**
```python
# مسروق من: MUSE sandbox lifecycle tools
class SandboxExecutor:
    def create_sandbox() → str         # sandbox_id
    def run(sandbox_id, code, args) → dict
    def upload(sandbox_id, file_path)
    def download(sandbox_id, file_path)
    def close(sandbox_id)
    # Implementation: subprocess in tmpdir (not Docker — free tier)
```

**genesis/tool_hub/__init__.py**
```python
# Clean public API
from genesis.tool_hub.registry import ToolRegistry, ToolSpec
from genesis.tool_hub.executor import SandboxExecutor

_registry = ToolRegistry()
# Auto-register all tools
_registry.register(WEB_SEARCH_TOOL)
_registry.register(CODE_EXEC_TOOL)
_registry.register(FILE_OPS_TOOL)
_registry.register(LLM_CALL_TOOL)

def get_tool(name: str) → ToolSpec: return _registry.get(name)
def invoke(name: str, args: dict) → dict: return _registry.invoke(name, args)
def catalog() → str: return _registry.catalog()
```

#### Integration في orchestrator.py
```python
# Section 3 (Prompts):
from genesis.tool_hub import catalog as tool_catalog
TOOL_CATALOG_SECTION = f"AVAILABLE TOOLS:\n{tool_catalog()}"
META_AGENT_PROMPT = TOOL_CATALOG_SECTION + "\n\n" + META_AGENT_PROMPT

# في target_agent.py template:
# from genesis.tool_hub import get_tool, invoke
# result = invoke("web_search", {"query": "...", "mode": "quick"})
```

#### Tests
```
tests/test_tool_hub.py  ← 35+ tests
  TestToolSpec
  TestToolRegistry
  TestSandboxExecutor
  TestWebSearchTool (wraps existing 39 tests)
  TestCatalogFormat
```

---

### PHASE 2: SKILL ENGINE — Core (أسبوع 2-3)

**الهدف:** MUSE lifecycle + SkillOps contract + EvoSkill frontier

#### الملفات المبنية

**genesis/skill_engine/skill.py**
```python
# مسروق من: MUSE (SKILL.md format) + SkillOps (P,O,A,V,F contract)

@dataclass  
class SkillContract:
    """SkillOps: (P, O, A, V, F)"""
    preconditions: list[str]     # P: متى تُستخدَم
    operation: str               # O: ماذا تفعل
    artifact_type: str           # A: ما تُنتج
    validator: str               # V: كيف تتحقق (أو "" = validation gap)
    failure_modes: list[str]     # F: أسباب الفشل

@dataclass
class Skill:
    """MUSE SKILL.md format + SkillOps contract"""
    # Identity
    name: str
    version: str
    domain: str                  # research | coding | analysis | ...
    task_types: list[str]
    
    # SKILL.md content
    description: str             # في catalog فقط (minimal)
    instructions: str            # body — loaded on demand
    
    # Contract (SkillOps)
    contract: SkillContract
    
    # Filesystem
    skill_dir: Path
    scripts_dir: Path
    tests_dir: Path
    resources_dir: Path
    memory_file: Path            # .memory.md (MUSE)
    
    # Metrics
    performance_score: float
    usage_count: int
    success_rate: float
    source_run: str
    source_gen: int
    created_at: datetime
    
    # Frontier tracking (EvoSkill)
    generation: int              # mutation depth from root
    parent_skill: str | None
    frontier_rank: int | None
    
    def read_memory(self) → str     # .memory.md content
    def append_memory(self, note: str)  # MUSE: accumulate experience
    def get_catalog_entry(self) → str   # name + description only
    def get_full_body(self) → str       # full instructions
    def to_tool_spec(self) → ToolSpec   # للـ ToolHub

class SkillFolder:
    """Creates skill folder from scratch"""
    @staticmethod
    def create(name, instructions, scripts={}, tests={}) → Path
    
    @staticmethod
    def from_path(path: Path) → Skill
    
    @staticmethod
    def validate_structure(path: Path) → list[str]  # validation errors
```

**genesis/skill_engine/library.py**
```python
# مسروق من: MUSE (lifecycle) + SkillOps (maintenance) + EvoSkill (frontier)

class SkillLibrary:
    """The skill bank — filesystem + SQLite"""
    
    skills_dir: Path             # genesis/skill_engine/skills/
    registry_db: Path            # skill_registry.db (gitignored)
    frontier: list[Skill]        # EvoSkill: top-K best skills
    frontier_k: int = 3
    
    # Core CRUD
    def register(self, skill: Skill) → bool    # create→eval→register loop
    def get(self, name: str) → Skill | None
    def update(self, skill: Skill)              # MUSE: update_skill
    def retire(self, name: str)                # SkillOps: retire action
    
    # Frontier (EvoSkill)
    def add_to_frontier(self, skill: Skill)
    def evict_weakest(self)                    # removes lowest score
    def get_frontier(self) → list[Skill]
    
    # Maintenance (SkillOps)
    def merge(self, skill_a: Skill, skill_b: Skill) → Skill
    def health_check(self) → HealthReport     # utility+redundancy+compat+risk+gap
    def run_maintenance(self) → int           # returns actions taken (O(N), ~0 LLM)
    
    # Catalog
    def get_catalog_yaml(self) → str          # minimal: name+description
    def get_full_catalog(self) → list[Skill]
    def rebuild_catalog(self)                 # regenerates catalog.yaml
    
    # Stats
    def get_stats(self) → dict
```

**genesis/skill_engine/evaluator.py**
```python
# مسروق من: MUSE (create→evaluate→register loop + sandbox testing)

class SkillEvaluator:
    """Runs tests before registering skill"""
    
    def run_tests(self, skill: Skill) → TestResult:
        """
        MUSE pattern: sandbox → pytest → pass/fail
        Implementation: subprocess tmpdir (not Docker)
        """
        # 1. Create isolated tmpdir
        # 2. Copy skill scripts/ + tests/
        # 3. Run: python -m pytest tests/ -q
        # 4. Parse results
        # 5. Return pass/fail + error_trace
    
    def validate_artifact(self, skill: Skill, artifact_path: str) → bool:
        """SkillOps: V validator"""
    
    def check_contract(self, skill: Skill, context: dict) → bool:
        """SkillOps: P precondition check"""

@dataclass
class TestResult:
    passed: bool
    tests_run: int
    failures: list[str]
    error_trace: str
    execution_time: float
```

**genesis/skill_engine/extractor.py**
```python
# مسروق من: MUSE (skill creation from agent) + EvoSkill (failure analysis)

class SkillExtractor:
    """Extracts skills from successful target_agent.py"""
    
    def extract_from_agent(
        self,
        agent_path: str,
        score: float,
        run_id: str,
        gen_id: int,
        llm_client: openai.OpenAI,
    ) → list[Skill]:
        """
        يقرأ target_agent.py الناجح
        يُحدّد الـ patterns المتكررة والمفيدة
        يُولّد SKILL.md لكل pattern
        """
        # 1. Parse agent code (AST)
        # 2. LLM: identify reusable patterns
        # 3. For each pattern → create Skill draft
        # 4. Evaluator.run_tests() → filter passing
        # 5. Return validated skills

class FailureCollector:
    """EvoSkill: collect failures for Proposer"""
    
    def collect(
        self,
        gen_dir: str,
        threshold: float = 0.6,
    ) → list[FailureCase]:
        """
        يقرأ open_task_eval.json + evaluation_results.json
        يُجمّع الحالات التي score < threshold
        يُعيد traces كاملة
        """

@dataclass
class FailureCase:
    gen: int
    question_or_task: str
    agent_output: str
    expected: str
    score: float
    error_trace: str
```

**genesis/skill_engine/graph.py**
```python
# مسروق من: SkillOps HSEG (dep/comp/red/alt edges)

class SkillGraph:
    """Hierarchical Skill Ecosystem Graph"""
    
    # Relations
    def add_dep(self, skill_i: str, skill_j: str)   # output of i → input of j
    def add_comp(self, skill_i: str, skill_j: str)  # type compatible
    def add_red(self, skill_i: str, skill_j: str)   # redundant (same interface)
    def add_alt(self, skill_i: str, skill_j: str)   # alternative (same goal)
    
    # Planning
    def find_plan(self, task: str, library: SkillLibrary) → list[Skill]:
        """
        Stage 1: BM25+semantic retrieval
        Stage 2: dependency stitching
        Stage 3: adapter insertion if needed
        """
    
    # Health
    def find_redundant(self) → list[tuple[str, str]]
    def find_compatibility_gaps(self) → list[tuple[str, str]]
    def find_validation_gaps(self) → list[str]
    
    # CGPD: propagate failure risk
    def propagate_risk(self) → dict[str, float]
```

**genesis/skill_engine/retriever.py**
```python
# مسروق من: SkillOps (hybrid BM25+semantic) + SAGE (keyword precision)

class SkillRetriever:
    """Hybrid retrieval: BM25 + semantic"""
    
    def retrieve(
        self,
        query: str,
        library: SkillLibrary,
        top_k: int = 3,
        lambda_bm25: float = 0.5,
    ) → list[Skill]:
        """
        r(s, q) = λ·BM25(s, q) + (1-λ)·semantic(s, q)
        Filter by preconditions
        Return top-k
        """
    
    def _bm25_score(self, skill: Skill, query: str) → float
    def _semantic_score(self, skill: Skill, query: str) → float
    def _check_preconditions(self, skill: Skill, context: dict) → bool
```

**genesis/skill_engine/evolver.py**
```python
# مسروق من: EvoSkill (3-agent loop + frontier)

class ProposerAgent:
    """EvoSkill Proposer: analyzes failures → proposes skills"""
    
    def __init__(self, llm_client, feedback_history: list = None)
    
    def propose(
        self,
        failures: list[FailureCase],
        existing_skills: list[Skill],
    ) → SkillProposal:
        """
        يُحلّل failures
        يُدقق existing skills
        يُقرّر: new_skill OR edit_existing
        يُضيف لـ feedback_history
        """

@dataclass
class SkillProposal:
    action: str               # "create" | "edit"
    target_skill: str | None  # إذا edit
    description: str
    rationale: str
    capability_gap: str

class SkillBuilderAgent:
    """EvoSkill Skill-Builder: materializes proposal → skill folder"""
    
    def __init__(self, llm_client)
    
    def materialize(
        self,
        proposal: SkillProposal,
        parent_skill: Skill | None = None,
    ) → Skill:
        """
        يُنشئ SKILL.md + scripts/ + tests/
        يُشغّل evaluator.run_tests()
        لو fail: يُصلح ويُعيد
        """

class EvoSkillLoop:
    """EvoSkill main loop"""
    
    def run(
        self,
        executor_results: list[dict],     # generation results
        library: SkillLibrary,
        graph: SkillGraph,
        proposer: ProposerAgent,
        builder: SkillBuilderAgent,
        evaluator: SkillEvaluator,
        iterations: int = 5,
        frontier_k: int = 3,
    ) → list[Skill]:
        """
        for t in 1..T:
            parent = round_robin(frontier)
            failures = collect_failures(parent)
            proposal = proposer.propose(failures, library)
            candidate = builder.materialize(proposal)
            if eval better than weakest frontier:
                add to frontier
        return frontier
        """
```

**genesis/skill_engine/__init__.py**
```python
# Clean public API — الـ orchestrator يستدعي هذا فقط

from .library import SkillLibrary
from .evaluator import SkillEvaluator
from .extractor import SkillExtractor, FailureCollector
from .retriever import SkillRetriever
from .graph import SkillGraph
from .evolver import EvoSkillLoop, ProposerAgent, SkillBuilderAgent

# Singleton instances
_library = SkillLibrary(skills_dir=Path("genesis/skill_engine/skills"))
_evaluator = SkillEvaluator()
_retriever = SkillRetriever()
_graph = SkillGraph()

def register(skill): return _library.register(skill)
def retrieve(query, top_k=3): return _retriever.retrieve(query, _library, top_k)
def execute(name, args): return _library.get(name).execute(args)
def get_catalog() → str: return _library.get_catalog_yaml()
def run_maintenance(): return _library.run_maintenance()
```

#### Integration في orchestrator.py
```python
# Section 3 (Prompts):
from genesis.skill_engine import get_catalog as skill_catalog
SKILL_SECTION = f"AVAILABLE SKILLS (use skill_use tool):\n{skill_catalog()}"
META_AGENT_PROMPT = SKILL_SECTION + "\n\n" + META_AGENT_PROMPT

# Section 5a.1 (after evaluation):
from genesis.skill_engine import register
from genesis.skill_engine.extractor import SkillExtractor
if overall_score > 70:  # threshold
    extractor = SkillExtractor()
    new_skills = extractor.extract_from_agent(
        target_agent_path, overall_score, run_id, current_gen, llm_client
    )
    for skill in new_skills:
        register(skill)
        logger.info(f"  ✅ New skill registered: {skill.name}")

# Section 5a.3 (after AlphaEvolve):
from genesis.skill_engine.evolver import EvoSkillLoop
evo_loop = EvoSkillLoop()
evolved_skills = evo_loop.run(
    executor_results=gen_results,
    library=_skill_library,
    ...
)
```

---

### PHASE 3: META ENGINE (أسبوع 4-5)

**الهدف:** TextGrad API حقيقي + EvoSkill Proposer يُحلّل trajectory

#### الملفات المبنية

**genesis/meta_engine/textgrad.py**
```python
# مسروق من: TextGrad (Stanford) — PyTorch-style API

@dataclass
class TextVariable:
    """A variable that can be optimized via textual gradients"""
    value: str                    # current value (agent code or prompt)
    requires_grad: bool = True
    role_description: str = ""   # helps LLM understand what to optimize
    gradient: str = ""           # textual gradient (filled by backward())
    grad_history: list[str] = field(default_factory=list)

class TextLoss:
    """LLM-based loss function"""
    def __init__(self, evaluation_instruction: str, llm_client)
    
    def __call__(self, variable: TextVariable) → TextVariable:
        """Forward pass: evaluate variable quality"""
        # LLM evaluates variable.value
        # Returns loss description as TextVariable
    
    def backward(self, loss: TextVariable, variable: TextVariable):
        """Backward pass: compute textual gradient"""
        # LLM generates: "what should change in variable to reduce loss?"
        # Stores in variable.gradient

class TGD:
    """Textual Gradient Descent optimizer"""
    def __init__(self, parameters: list[TextVariable], llm_client)
    
    def step(self):
        """Apply gradients: update each variable"""
        for param in self.parameters:
            if param.requires_grad and param.gradient:
                param.value = self._apply_gradient(param.value, param.gradient)
    
    def zero_grad(self):
        for param in self.parameters:
            param.gradient = ""
    
    def _apply_gradient(self, value: str, gradient: str) → str:
        """LLM applies the gradient to update the variable"""
```

**genesis/meta_engine/trajectory.py**
```python
# مسروق من: ExpeL (trajectory analysis) + TextGrad (computation graph)

@dataclass
class GenerationPoint:
    gen: int
    score: float
    hallucination_rate: float
    ladder_level: int
    key_changes: list[str]        # diff من Gen N-1
    winning_elements: list[str]   # ما نجح
    losing_elements: list[str]    # ما فشل
    agent_code_hash: str          # للـ comparison

class GenerationTrajectory:
    """Full run history as computation graph (TextGrad inspired)"""
    
    points: list[GenerationPoint]
    
    def find_peak(self) → GenerationPoint
    def find_regression(self) → tuple | None
    def find_plateau(self, window=3) → list[GenerationPoint]
    
    def extract_winning_pattern(self) → str:
        """ما الذي أدى للتحسين؟ (textual gradient concept)"""
    
    def extract_delta(self, gen_a: int, gen_b: int) → str:
        """ما الذي تغيّر بين نقطتين؟"""
    
    def compute_textual_gradient(self, llm_client) → str:
        """
        TextGrad: backpropagate through trajectory
        Input: full history
        Output: "textual gradient" — ما الذي يجب تغييره
        """
    
    @classmethod
    def load_from_run(cls, run_dir: str, current_gen: int) → "GenerationTrajectory"
```

**genesis/meta_engine/optimizer.py**
```python
# يجمع كل شيء

class MetaOptimizer:
    """Main entry point for Meta Engine"""
    
    def __init__(self, llm_client)
    
    def run(
        self,
        run_dir: str,
        current_gen: int,
        skill_library: SkillLibrary,
    ) → MetaResult:
        """
        1. Load trajectory
        2. Compute textual gradient (TextGrad backward)
        3. Get relevant skills from library
        4. Synthesize meta instruction
        5. Return for feedback prompt injection
        """
    
    def compute_textual_gradient(self, trajectory: GenerationTrajectory) → str
    
    def synthesize_meta_instruction(
        self,
        trajectory: GenerationTrajectory,
        gradient: str,
        skills: list[Skill],
    ) → str:
        """Returns text to inject in FEEDBACK_AGENT_PROMPT"""

@dataclass
class MetaResult:
    trajectory_summary: str
    textual_gradient: str
    winning_pattern: str
    losing_pattern: str
    meta_instruction: str     # للـ feedback prompt
    confidence: float
    artifacts_path: str       # meta_optimization.json
```

#### Integration في orchestrator.py
```python
# Section 5a.5 (NEW — بعد Regime, قبل Feedback):
from genesis.meta_engine import MetaOptimizer

meta_opt = MetaOptimizer(llm_client=_meta_llm)
meta_result = meta_opt.run(RUN_DIRECTORY, current_gen, skill_library)

# يدخل FEEDBACK_AGENT_PROMPT:
META_SECTION = meta_result.meta_instruction
SPIN_SECTION = spin_section + regime_section + enhanced_section + META_SECTION
```

---

### PHASE 4: AGENT HUB (أسبوع 6-7)

**الهدف:** AgentSpec كامل + Soul files + Memory architecture

#### الملفات المبنية

**genesis/agent_hub/soul/soul.py**
```python
# مسروق من: OpenClaw SOUL.md + BDI Architecture

@dataclass
class AgentSoul:
    name: str
    role: str
    version: str
    
    # SOUL.md sections
    core_values: list[str]
    constitution: list[str]       # non-negotiable rules
    communication_style: str
    example_responses: list[dict]  # good/bad examples
    
    # From AGENTS.md (separate!)
    behavior_guidelines: list[str]
    safety_rules: list[str]
    tool_permissions: dict[str, list[str]]
    
    # Cost guardrails
    max_llm_calls: int = 20
    max_web_searches: int = 15
    max_cost_usd: float = 1.0
    
    # Memory rules
    memory_expiry_days: int = 30
    
    def to_soul_md(self) → str           # SOUL.md format
    def to_agents_md(self) → str         # AGENTS.md format (behavior)
    def validate_action(self, action) → tuple[bool, str]  # BDI adoption filter
    
    @classmethod
    def load(cls, soul_dir: Path) → "AgentSoul"  # loads SOUL.md + AGENTS.md
    def save(self, soul_dir: Path)
```

**genesis/agent_hub/memory/manager.py**
```python
# مسروق من: MAGMA (graph structure) + MemGPT (OS metaphor) + MemoryOS (hierarchy)

class AgentMemoryManager:
    """4-tier memory architecture"""
    
    working: WorkingMemory       # context window (RAM)
    episodic: EpisodicMemory     # timestamped experiences (Disk)
    semantic: SemanticMemory     # extracted facts (Disk)
    procedural: ProceduralMemory # = SkillLibrary bridge
    
    def read(self, query: str, intent: str) → MemoryResult
    def write(self, content: str, memory_type: str, metadata: dict)
    def consolidate(self)  # episodic → semantic (nightly)
    def expire(self)       # remove old entries (soul.memory_expiry_days)
    def get_context(self) → str  # للـ LLM prompt injection
```

**genesis/agent_hub/agent.py**
```python
# الكيان الكامل

@dataclass
class AgentSpec:
    id: str
    name: str
    version: str
    created_at: datetime
    
    # Sections
    soul: AgentSoul
    memory_config: dict
    tool_names: list[str]
    skill_names: list[str]
    
    # BDI Runtime State
    beliefs: dict = field(default_factory=dict)
    desires: list[str] = field(default_factory=list)
    intentions: list[str] = field(default_factory=list)
    
    # GENESIS Pipeline Config
    pipeline_config: dict
    run_history: list[str] = field(default_factory=list)
    
    def to_system_prompt(self) → str   # soul + tools catalog + skills catalog
    def to_dict(self) → dict           # JSON-serializable (vibe web foundation)
    def update_beliefs(self, new_beliefs: dict)  # BDI update after each gen
    
    @classmethod
    def for_task(cls, task_name: str, soul_type: str = "research") → "AgentSpec"
```

**genesis/agent_hub/registry.py**
```python
# Foundation للـ vibe web

class AgentRegistry:
    db: SQLite
    agents_dir: Path
    
    def create(self, spec: AgentSpec) → str
    def read(self, agent_id: str) → AgentSpec
    def update(self, agent_id: str, spec: AgentSpec)
    def delete(self, agent_id: str)
    def list(self, filter: dict = None) → list[AgentSpec]
    def get_catalog(self) → list[dict]   # minimal metadata (REST API ready)
```

#### Integration في orchestrator.py
```python
# Section 0 (قبل Goal Spec):
from genesis.agent_hub import AgentRegistry
from genesis.agent_hub.agent import AgentSpec

agent_registry = AgentRegistry()
agent_spec = AgentSpec.for_task(task_name=os.path.basename(task_dir))

# Soul → META_AGENT_PROMPT
soul_section = agent_spec.soul.to_soul_md()
META_AGENT_PROMPT = soul_section + "\n\n" + META_AGENT_PROMPT

# After each gen → update BDI beliefs
agent_spec.update_beliefs({
    "last_score": overall_score,
    "hallucination_rate": hallucination_rate,
    "current_gen": current_gen,
})
agent_registry.update(agent_spec.id, agent_spec)
```

---

### PHASE 5: SAFETY + TELEMETRY (أسبوع 8)

**genesis/safety_engine/**
```python
class BudgetGuard:
    max_cost_usd: float
    max_time_sec: float
    max_api_calls: int
    
    def check(self, current: BudgetState) → GuardResult  # warn/pause/halt

class HallucinationGuard:
    threshold: float = 0.85
    def check(self, hallucination_rate: float) → GuardResult

class EscalationPolicy:
    WARN → log warning
    PAUSE → wait for human input (future)
    HALT → raise HaltException

# Integration: Section 5 start (before each generation)
from genesis.safety_engine import check_all_guards
result = check_all_guards(run_state)
if result.action == "HALT":
    raise SystemExit("Safety halt triggered")
```

**genesis/telemetry/**
```python
class TelemetryEvent:
    timestamp: datetime
    section: str           # "5a.1", "INTENT_ENGINE", etc.
    event_type: str        # section_start | section_end | llm_call | error | signal
    data: dict
    duration_ms: float | None

class RunTelemetry:
    run_id: str
    events: list[TelemetryEvent]
    
    def log(self, event_type, section, data)
    def save(self, path: str)  # run_telemetry.json
    def summary(self) → dict   # per-section timings + costs

# Integration: في كل section في orchestrator
telemetry.log("section_start", "5a.1", {"gen": current_gen})
# ... section code ...
telemetry.log("section_end", "5a.1", {"score": score, "duration": t})
```

---

### ما يُضاف زيادة على الخطة (التنظيم الاحترافي)

#### 1. genesis/tool_hub/tools/skill_use.py (الأهم)
```python
# يُمكّن الـ agent يستدعي skill مباشرة
SKILL_USE_TOOL = ToolSpec(
    name="skill_use",
    description="Execute a proven skill from the skill library",
    input_schema={"skill_name": str, "context": dict},
    output_schema={"result": any, "memory_note": str},
    executor=lambda args: _skill_library.execute(args["skill_name"], args["context"]),
)
```

#### 2. genesis/skill_engine/skills/web_search_arabic/ (أول skill حقيقية)
```
web_search_arabic/
├── SKILL.md        ← instructions for Arabic research with credibility
├── scripts/
│   └── search.py  ← wraps genesis.tool_hub.invoke("web_search", ...)
├── tests/
│   └── test_search.py  ← validates: returns results + logs evidence
└── .memory.md      ← ابدأ فاضي، يتراكم مع الاستخدام
```

#### 3. genesis/__init__.py (package-level imports)
```python
# الـ orchestrator يعمل import واحد فقط:
from genesis import ToolHub, SkillEngine, MetaEngine, AgentHub, SafetyEngine

# وليس:
from genesis.tool_hub import ...
from genesis.skill_engine import ...
# etc.
```

#### 4. Schema Registry (artifact versioning)
```python
# genesis/schemas/
#   tool_spec.v1.json
#   skill.v1.json
#   agent_spec.v1.json
#   meta_result.v1.json

# كل artifact له:
{
    "schema_version": "1.0",
    "created_by": "SKILL_ENGINE",
    "created_at": "...",
    ...
}
```

#### 5. backward_compat.py (لا يكسر الكود القديم)
```python
# genesis/backward_compat.py
# يُبقي الـ imports القديمة تعمل:

# القديم (لا يزال يعمل):
from genesis.tools.web_search import web_search  # ← يبقى

# الجديد (يُنصح به):
from genesis.tool_hub import invoke
result = invoke("web_search", {"query": "...", "mode": "quick"})
```

---

## Tests الكاملة المطلوبة

```
tests/
  test_tool_hub.py           ← 35 tests (Phase 1)
  test_skill_engine.py       ← 60 tests (Phase 2)
    TestSkill
    TestSkillLibrary
    TestSkillEvaluator
    TestSkillExtractor
    TestSkillGraph
    TestSkillRetriever
    TestEvoSkillLoop
  test_meta_engine.py        ← 40 tests (Phase 3)
    TestTextVariable
    TestTextLoss
    TestTGD
    TestGenerationTrajectory
    TestMetaOptimizer
  test_agent_hub.py          ← 50 tests (Phase 4)
    TestAgentSoul
    TestAgentMemoryManager
    TestAgentSpec
    TestAgentRegistry
  test_safety_engine.py      ← 25 tests (Phase 5)
  test_telemetry.py          ← 20 tests (Phase 5)

TOTAL NEW: ~230 tests
TOTAL COMBINED: ~1170 tests
```

---

## الجدول الزمني النهائي

```
Week 1:  TOOL HUB — registry + executor + wrap existing tools
Week 2:  SKILL ENGINE Core — skill.py + library.py + evaluator.py
Week 3:  SKILL ENGINE Advanced — graph.py + retriever.py + extractor.py
Week 4:  SKILL ENGINE Evolution — evolver.py (3-agent EvoSkill loop)
Week 5:  META ENGINE — textgrad.py + trajectory.py + optimizer.py
Week 6:  AGENT HUB — soul.py + memory/ + agent.py
Week 7:  AGENT HUB — registry.py + Integration في orchestrator
Week 8:  SAFETY + TELEMETRY + Schema Registry + backward_compat
Week 9:  Integration tests + first real run with full stack
Week 10: Architecture Evolution planning (Phase D — docs only)
```

---

## ملخص — ما يُبنى جديداً

```
جديد كلياً (❌ → ✅):
  genesis/tool_hub/           ← Tool Hub section
  genesis/skill_engine/       ← Skill Engine section (full lifecycle)
  genesis/meta_engine/        ← Meta Engine section (TextGrad)
  genesis/agent_hub/          ← Agent Hub section
  genesis/safety_engine/      ← Safety Engine section
  genesis/telemetry/          ← Telemetry section
  genesis/schemas/            ← Schema Registry
  genesis/__init__.py         ← Package-level clean imports

يُطوَّر (⚠️ → ✅):
  genesis/tools/web_search.py ← يُبقى + يُغلَّف في tool_hub
  genesis/orchestrator.py     ← +6 new imports, no core change
  genesis/goal_specification.py ← يُبقى as INTENT ENGINE
  genesis/research_memory.py  ← يُبقى + يُدمج مع MEMORY ENGINE

لا يتغير (✅ → ✅):
  genesis/constitutional_evaluator.py
  genesis/open_task_evaluator.py
  genesis/context_manager.py
  genesis/enhanced_pipeline_bridge.py
  genesis/spin_feedback.py
  genesis/cognitive_bridge.py
  genesis/llm_helpers.py
  genesis/util.py
  virtual_genesis/ (كل شيء)
  tests/ (كل الـ 937 tests تبقى)
```
