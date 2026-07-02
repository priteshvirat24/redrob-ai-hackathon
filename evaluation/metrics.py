"""
Evaluation Metrics.
Calculates NDCG, Score Spread, and simple accuracy for ablation tests.
"""

import math
from typing import List
from config.types import ScoredCandidate
import logging

logger = logging.getLogger(__name__)

def dcg_at_k(scores: List[float], k: int) -> float:
    scores = scores[:k]
    return sum([score / math.log2(i + 2) for i, score in enumerate(scores)])

def ndcg_at_k(actual_scores: List[float], ideal_scores: List[float], k: int) -> float:
    dcg = dcg_at_k(actual_scores, k)
    idcg = dcg_at_k(ideal_scores, k)
    if idcg == 0:
        return 0.0
    return dcg / idcg

def evaluate_ranking(scored_candidates: List[ScoredCandidate], k: int = 100) -> dict:
    """Returns various metrics for a given ranking."""
    if not scored_candidates:
        return {}

    # For NDCG, we assume the true relevance is the computed score.
    # We compare the current ordering to a perfect ordering.
    actual_scores = [c.score for c in scored_candidates]
    ideal_scores = sorted(actual_scores, reverse=True)
    
    ndcg = ndcg_at_k(actual_scores, ideal_scores, k)
    top_k_scores = ideal_scores[:k]
    spread = max(top_k_scores) - min(top_k_scores) if top_k_scores else 0.0
    
    return {
        f"NDCG@{k}": ndcg,
        f"Score Spread (Top {k})": spread,
        "Total Candidates": len(scored_candidates),
        "Max Score": max(actual_scores),
    }

def print_evaluation(metrics: dict, title: str = "Evaluation"):
    logger.info(f"=== {title} ===")
    for k, v in metrics.items():
        if isinstance(v, float):
            logger.info(f"{k:.<25} {v:.4f}")
        else:
            logger.info(f"{k:.<25} {v}")
    logger.info("========================")
