# AI Recruiting Copilot — Redrob Hackathon Submission

An advanced, multi-agent AI system designed to rank 100,000 candidates for a Senior AI Engineer role under strict compute constraints.

## Architecture

This solution uses a **two-phase architecture** to meet the 5-minute CPU-only constraint while maintaining high semantic accuracy:

1. **Pre-computation Phase (`backend/precompute.py`)**: Runs offline to extract structured features, compute semantic embeddings (sentence-transformers), analyze career coherence, and identify honeypots/keyword stuffers.
2. **Ranking Phase (`backend/rank.py`)**: The fast, 5-minute CPU pipeline that loads pre-computed features, computes the final composite score using a multi-signal scoring algorithm, generates specific reasoning, and writes the `submission.csv`.

## Multi-Agent System

- **Candidate Profiler Agent**: Analyzes career trajectory, company types, and title relevance.
- **Honeypot Detector Agent**: Identifies trap candidates (duration mismatches, 0-month expert skills).
- **Skill Graph Agent**: Maps candidate skills against JD absolute and preferred requirements, prioritizing verified assessment scores.
- **Behavioral Scorer Agent**: Calculates a multiplier based on recruiter response rate, recency, and notice period.
- **Reranker Agent**: Fuses all signals (semantic, title, skill, experience, coherence, behavioral) into a final score.
- **Explainability Agent**: Generates specific, factual, non-templated reasoning for the top 100 candidates.

## How to Run the Ranking Pipeline (Evaluation Step)

```bash
# 1. Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# 2. Run the 5-minute ranking pipeline
time python backend/rank.py \
  --candidates "[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl" \
  --out submission.csv

# 3. Validate
python3 "[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/validate_submission.py" submission.csv
```

## How to Run the UI Demo

The submission includes a polished Next.js + FastAPI dashboard to demonstrate the system visually.

```bash
# Using Docker Compose
docker-compose up --build
```
Navigate to `http://localhost:3000` to view the AI Recruiting Copilot dashboard.
