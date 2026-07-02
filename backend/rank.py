"""
Main Ranking Pipeline.
Must run within 5 minutes on CPU, 16GB RAM, NO network.
Loads pre-computed features and outputs submission.csv.
"""

import sys
import os
import csv
import pickle
import time
import argparse
from pathlib import Path
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.config import PRECOMPUTED_DIR, ScoringWeights
from backend.agents.reranker import compute_final_score
from backend.agents.explainability import generate_reasoning
from backend.data.loader import iter_candidates
from backend.core.types import ScoredCandidate

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_precomputed_features():
    """Load pre-computed CandidateFeatures dict."""
    features_path = PRECOMPUTED_DIR / "features.pkl"
    if not features_path.exists():
        logger.error(f"Pre-computed features not found at {features_path}")
        logger.error("You must run 'python backend/precompute.py' first!")
        sys.exit(1)
        
    logger.info("Loading pre-computed features...")
    with open(features_path, "rb") as f:
        features_dict = pickle.load(f)
    return features_dict


def run_ranking(candidates_file, output_file):
    """Run the 5-min ranking pipeline."""
    start_time = time.time()
    
    # 1. Load features
    features_dict = load_precomputed_features()
    
    # 2. Score candidates
    weights = ScoringWeights()
    scored_candidates = []
    
    logger.info("Scoring candidates...")
    # We iterate through the raw candidates.jsonl to ensure we match the exact IDs and get raw data for reasoning
    for candidate in iter_candidates(candidates_file):
        cid = candidate.candidate_id
        if cid not in features_dict:
            logger.warning(f"No pre-computed features for {cid}, skipping.")
            continue
            
        features = features_dict[cid]
        
        # Calculate final composite score
        score, breakdown = compute_final_score(features, weights)
        
        scored = ScoredCandidate(
            candidate_id=cid,
            rank=0, # Will be set during sorting
            score=score,
            reasoning="", # Will be set for top 100
            features=features,
            score_breakdown=breakdown
        )
        scored_candidates.append(scored)
        
    # 3. Sort candidates (Primary: score descending, Secondary: ID ascending to break ties)
    logger.info("Sorting candidates...")
    # Round to 4 decimal places before sorting to ensure tie-breaks match the output CSV
    for c in scored_candidates:
        c.score = round(c.score, 4)
        
    scored_candidates.sort(key=lambda x: (-x.score, x.candidate_id))
    
    # 4. Take top 100 and generate reasoning
    top_100 = scored_candidates[:100]
    
    logger.info("Generating reasoning for top 100...")
    # Need to load the raw Candidate objects for the top 100 to get exact strings for reasoning
    top_cids = {c.candidate_id for c in top_100}
    top_raw_candidates = {}
    for candidate in iter_candidates(candidates_file):
        if candidate.candidate_id in top_cids:
            top_raw_candidates[candidate.candidate_id] = candidate
            
    for i, scored in enumerate(top_100):
        scored.rank = i + 1
        raw_cand = top_raw_candidates[scored.candidate_id]
        scored.reasoning = generate_reasoning(raw_cand, scored.features, scored.rank, scored.score)
        
    # 5. Write submission CSV
    logger.info(f"Writing results to {output_file}...")
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for c in top_100:
            # Format score to 4 decimal places
            writer.writerow([c.candidate_id, c.rank, f"{c.score:.4f}", c.reasoning])
            
    elapsed = time.time() - start_time
    logger.info(f"Ranking complete in {elapsed:.2f} seconds!")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Redrob Hackathon Ranker")
    parser.add_argument("--candidates", type=str, required=True, help="Path to candidates.jsonl")
    parser.add_argument("--out", type=str, required=True, help="Path to output submission.csv")
    
    args = parser.parse_args()
    run_ranking(args.candidates, args.out)
