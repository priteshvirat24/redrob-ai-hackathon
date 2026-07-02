"""
AI Evaluation Lab.
A CLI tool to run ablation tests and see metric changes live.
"""

import sys
import os
import argparse
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ranking.features.registry import FeatureRegistry
from evaluation.metrics import evaluate_ranking, print_evaluation
from pipelines.offline_rank import run_ranking, ensure_precomputed

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def run_ablation(candidates_file: str, toggle_feature: str = None):
    logger.info("\n=== AI Evaluation Lab ===")
    
    # Run Baseline (All features ON)
    logger.info("Running Baseline (All Features ON)...")
    baseline_scores = run_ranking(candidates_file, "baseline.csv", quiet=True)
    baseline_metrics = evaluate_ranking(baseline_scores)
    
    if not toggle_feature:
        print_evaluation(baseline_metrics, "Baseline Metrics")
        return

    # Toggle Feature OFF
    logger.info(f"\nToggling Feature '{toggle_feature}' OFF...")
    FeatureRegistry.toggle(toggle_feature, False)
    
    ablation_scores = run_ranking(candidates_file, "ablation.csv", quiet=True)
    ablation_metrics = evaluate_ranking(ablation_scores)
    
    # Restore Feature
    FeatureRegistry.toggle(toggle_feature, True)
    
    # Print Comparison
    b_ndcg = baseline_metrics.get("NDCG@100", 0.0)
    a_ndcg = ablation_metrics.get("NDCG@100", 0.0)
    diff = b_ndcg - a_ndcg
    pct = (diff / a_ndcg * 100) if a_ndcg > 0 else 0.0
    
    logger.info(f"\n--- Comparison for {toggle_feature} ---")
    logger.info(f"Without {toggle_feature} (NDCG@100): {a_ndcg:.4f}")
    logger.info(f"With {toggle_feature} (NDCG@100):    {b_ndcg:.4f}")
    sign = "+" if diff > 0 else ""
    logger.info(f"Improvement:            {sign}{diff:.4f} ({sign}{pct:.1f}%)")
    logger.info("----------------------------------\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Evaluation Lab")
    parser.add_argument("--candidates", type=str, default="datasets/tiny/candidates.jsonl")
    parser.add_argument("--ablate", type=str, help="Feature name to toggle OFF (e.g. semantic_score)")
    args = parser.parse_args()
    
    # Warm up cache
    ensure_precomputed(args.candidates)
    
    run_ablation(args.candidates, args.ablate)
