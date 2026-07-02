"""
FastAPI Backend for the AI Recruiting Copilot.
Serves candidate search, ranking results, and analytics to the frontend.
Only loads top-100 candidate data, not all 100K.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import os
import sys
import csv
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Global state
features_dict = {}
raw_candidates = {}
top_100_results = []


def _load_data():
    """Load submission CSV and raw candidate data for top 100 only."""
    global features_dict, raw_candidates, top_100_results
    import pickle
    from config.settings import PRECOMPUTED_DIR

    # Load features (only if available)
    features_path = PRECOMPUTED_DIR / "features.pkl"
    if features_path.exists():
        with open(features_path, "rb") as f:
            features_dict = pickle.load(f)

    # Load top 100 results from submission.csv if it exists
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    submission_path = os.path.join(project_root, "submission.csv")
    if os.path.exists(submission_path):
        with open(submission_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                top_100_results.append({
                    "candidate_id": row["candidate_id"],
                    "rank": int(row["rank"]),
                    "score": float(row["score"]),
                    "reasoning": row["reasoning"],
                })

    # Load raw candidates for top 100 ONLY (not all 100K)
    top_cids = {r["candidate_id"] for r in top_100_results}
    if top_cids:
        from intelligence.feature_store.loader import iter_candidates
        for c in iter_candidates():
            if c.candidate_id in top_cids:
                raw_candidates[c.candidate_id] = c
            if len(raw_candidates) >= len(top_cids):
                break


@asynccontextmanager
async def lifespan(app: FastAPI):
    _load_data()
    yield


app = FastAPI(title="AI Recruiting Copilot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/candidates/top")
def get_top_candidates(limit: int = 10, offset: int = 0):
    """Return top candidates with full profile info."""
    paginated = top_100_results[offset: offset + limit]

    results = []
    for r in paginated:
        cid = r["candidate_id"]
        feat = features_dict.get(cid)
        raw_cand = raw_candidates.get(cid)

        entry = {
            "candidate_id": cid,
            "rank": r["rank"],
            "score": r["score"],
            "reasoning": r["reasoning"],
        }

        if raw_cand:
            entry["profile"] = {
                "anonymized_name": raw_cand.profile.anonymized_name,
                "headline": raw_cand.profile.headline,
                "current_title": raw_cand.profile.current_title,
                "location": raw_cand.profile.location,
                "years_of_experience": raw_cand.profile.years_of_experience,
            }
            entry["skills"] = [{"name": s.name, "proficiency": s.proficiency} for s in raw_cand.skills[:10]]

        if feat:
            entry["features"] = {
                "is_india": feat.is_india,
                "behavioral_score": feat.behavioral_score,
                "title_tier": feat.title_tier,
                "skill_match_score": feat.skill_match_score,
            }

        results.append(entry)

    return {"candidates": results, "total": len(top_100_results)}


@app.get("/api/candidates/{candidate_id}")
def get_candidate(candidate_id: str):
    """Get full candidate details."""
    if candidate_id not in raw_candidates:
        raise HTTPException(status_code=404, detail="Candidate not found in top 100")

    raw_cand = raw_candidates[candidate_id]
    feat = features_dict.get(candidate_id)
    rank_info = next((r for r in top_100_results if r["candidate_id"] == candidate_id), None)

    return {
        "candidate_id": candidate_id,
        "rank_info": rank_info,
        "features": {
            "title_tier": feat.title_tier if feat else None,
            "behavioral_score": feat.behavioral_score if feat else None,
            "skill_match_score": feat.skill_match_score if feat else None,
            "semantic_score": feat.semantic_score if feat else None,
        } if feat else None,
    }


@app.get("/api/analytics")
def get_analytics():
    """Dashboard analytics computed from real data."""
    if not top_100_results:
        return {"total_ranked": 0, "avg_score": 0, "score_band": [0, 0]}

    scores = [r["score"] for r in top_100_results]
    return {
        "total_ranked": len(top_100_results),
        "avg_score": sum(scores) / len(scores),
        "score_band": [min(scores), max(scores)],
        "score_spread": max(scores) - min(scores),
    }
