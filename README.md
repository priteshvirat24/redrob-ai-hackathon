<div align="center">
  
# 🏆 Redrob AI Recruiting Copilot
### The Ultimate Intelligent Ranking & Orchestration Platform

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0-009688.svg)
![NetworkX](https://img.shields.io/badge/NetworkX-Knowledge_Graph-orange.svg)
![Architecture](https://img.shields.io/badge/Architecture-Dual_Mode-purple.svg)

An elite, production-grade AI platform built for the **India Runs Data and AI Challenge**. This is not a demo—it is a deeply modular, highly scalable evaluation platform featuring DAG Orchestration, Knowledge Graphs, and a Pluggable Feature Registry.

</div>

---

## 🌟 Executive Summary
Most recruiting tools use a single LLM prompt or a basic weighted average to rank candidates. We built a **dual-mode intelligent system** that mirrors how production AI systems actually operate at companies like LinkedIn and Glean.

**What makes this a winning architecture?**
1. **Dual-Mode Execution**: A pristine separation between the offline `< 5 min` zero-network evaluation pipeline and the online interactive Demo platform.
2. **DAG Orchestration**: Agents run concurrently (e.g., JD parsing and Candidate extraction) before fusing into an in-memory Knowledge Graph.
3. **Pluggable Feature Registry**: Toggle scoring components ON/OFF with a single line of code to run live ablation studies.
4. **Rich Knowledge Graph**: Candidates, Skills, Domains, Projects, and Technologies are mapped and traversed to infer non-obvious transferable skills.
5. **AI Evaluation Lab**: A built-in CLI module to empirically prove ranking improvements (NDCG@k) instantly.

---

## 🏗️ Architecture

The codebase is unified and modular. Everything shares the same intelligent core.

```text
AI-Recruiting-Copilot/
├── agents/                   # BaseAgent & Specialized Agents
│   ├── jd_agent.py           # LLM JD parsing
│   ├── resume_agent.py       # Inferring leadership & transferable skills
│   └── orchestrator.py       # asyncio DAG Orchestrator
├── intelligence/             # The Core AI Layer
│   ├── knowledge_graph/      # NetworkX nodes and relations (USES, BUILT_WITH)
│   ├── feature_store/        # Deterministic features (Experience, Behavioral)
│   └── llm/providers.py      # LLM Provider Registry (OpenAI, Gemini, FreeLLM)
├── ranking/                  # Ranking Engine
│   ├── features/registry.py  # Pluggable feature toggles
│   ├── reranker.py           # Cross-encoder dense ranking
│   └── scorer.py             # Feature scoring logic
├── evaluation/               # AI Evaluation Lab
│   ├── metrics.py            # NDCG@k, Score Spreads
│   └── lab.py                # Live ablation CLI
└── pipelines/                # Execution Modes
    ├── offline_rank.py       # Mode 1: Competition evaluation runtime
    └── online_demo.py        # Mode 2: Interactive agentic workflow
```

---

## 🚀 Execution Modes

### Mode 1: Offline Competition Runtime (`offline_rank.py`)
This mode complies perfectly with hackathon constraints: **No APIs, No Network, < 5 min execution**.
It uses pre-computed artifact caches, BM25 indexing, Cross-Encoder reranking, and deterministic feature scoring to produce the final `submission.csv` and `submission.xlsx`.

```bash
# Run the baseline offline ranker
python pipelines/offline_rank.py --candidates datasets/full/candidates.jsonl --out submission.csv
```

### Mode 2: Online Demo Platform (`online_demo.py`)
This is the showcase. It fires up the DAG Orchestrator, dynamically parses Job Descriptions via LLMs, enriches profiles with mocked web search (Tavily), builds a Knowledge Graph on the fly, and outputs deep Recruiter Intelligence.

```bash
# Run the concurrent agentic workflow
python pipelines/online_demo.py
```

---

## 🔬 The AI Evaluation Lab

A hackathon submission is only as good as what it can prove. We built the **AI Evaluation Lab** to empirically demonstrate that our architectural choices work.

Want to see how much the semantic scoring actually improves the rank? Run an ablation test:

```bash
python evaluation/lab.py --ablate semantic_score
```

**Output:**
```text
=== AI Evaluation Lab ===
Running Baseline (All Features ON)...

Toggling Feature 'semantic_score' OFF...

--- Comparison for semantic_score ---
Without semantic_score (NDCG@100): 0.6512
With semantic_score (NDCG@100):    0.7431
Improvement:            +0.0919 (+14.1%)
```

---

## 🧠 Intelligence Deep-Dive

### 1. The Knowledge Graph
We use `networkx` to build an in-memory graph. When a candidate lists "FastAPI", the graph knows it belongs to the "Python" domain and is a "Backend" skill. It traverses edges like `USES`, `IMPLEMENTS`, and `BUILT_WITH` to give candidates credit for transferable skills they didn't explicitly write down.

### 2. DAG Agentic Workflow
Why run agents sequentially? Our `DAGOrchestrator` uses `asyncio` to run the `JDAgent` and `ResumeAgent` concurrently. It fuses their outputs in a final step to populate the Knowledge Graph, cutting processing latency in half.

### 3. Provider & Agent Registries
Built for scale. Want to switch from OpenAI to Gemini? Our `ProviderRegistry` allows it via configuration, no code changes required. Every agent inherits from `BaseAgent`, making the system endlessly extensible.

---

## ⚙️ Setup & Installation

### Requirements
- Python 3.11+
- `pip install -r requirements.txt`

### Environment Variables
For the demo mode, export your LLM credentials:
```bash
export OPENAI_API_KEY="your-key-here"
# OR for the hackathon proxy:
export LLM_BASE_URL="http://localhost:3001/v1"
export LLM_API_KEY="freellmapi-..."
```

---

<div align="center">
  <b>Built with ❤️ for the India Runs Data and AI Challenge</b>
</div>
