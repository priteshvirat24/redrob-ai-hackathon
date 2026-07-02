"""
Reranker Agent.
Combines all computed features and scores into a final composite rank.
Uses graded penalties instead of hard multiplication-to-zero.
"""

import logging
from typing import Dict, Tuple
from config.types import Candidate, CandidateFeatures, ScoredCandidate
from config.settings import ScoringWeights

logger = logging.getLogger(__name__)


def compute_final_score(features: CandidateFeatures, weights: ScoringWeights) -> Tuple[float, Dict[str, float]]:
    """Compute the final score and return breakdown."""

    # 1. Base components
    semantic = features.semantic_score * weights.semantic_match

    # Scale title tier (1-5) to 0.0-1.0
    title_norm = (features.title_tier - 1) / 4.0
    title = title_norm * weights.title_relevance

    skills = features.skill_match_score * weights.skill_match
    experience = features.experience_fit_score * weights.experience_fit
    coherence = features.career_progression_score * weights.career_coherence
    education = features.education_score * weights.education
    behavioral = features.behavioral_score * weights.behavioral

    raw_score = semantic + title + skills + experience + coherence + education + behavioral

    # 2. Graded penalties
    multiplier = 1.0

    # Honeypot: hard zero only when honeypot_score > 0.7; otherwise graded
    if features.honeypot_score > 0.7:
        multiplier = 0.0
    elif features.honeypot_score > 0.0:
        multiplier *= (1.0 - 0.5 * features.honeypot_score)

    # Consulting-only career (JD disqualifier, but softer than zero)
    if features.has_consulting_only_career:
        multiplier *= 0.15

    # Title chaser
    if features.is_title_chaser:
        multiplier *= 0.85

    # Non-India (no visa sponsorship)
    if not features.is_india:
        multiplier *= 0.85

    final = raw_score * multiplier

    breakdown = {
        "semantic": semantic,
        "title": title,
        "skills": skills,
        "experience": experience,
        "coherence": coherence,
        "education": education,
        "behavioral": behavioral,
        "raw_total": raw_score,
        "multiplier": multiplier,
    }

    features.final_score = final
    return final, breakdown
