"""
Reranker Agent.
Combines all computed features and scores into a final composite rank.
"""

import logging
from typing import Dict, Tuple
from backend.core.types import Candidate, CandidateFeatures, ScoredCandidate
from backend.core.config import ScoringWeights

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
    
    # 2. Multipliers / Penalties
    multiplier = 1.0
    
    if features.is_honeypot:
        multiplier = 0.0
        
    if features.has_consulting_only_career:
        multiplier *= 0.1 # Explicit JD disqualifier
        
    if features.is_title_chaser:
        multiplier *= 0.8
        
    if not features.is_india:
        multiplier *= 0.8 # No visa sponsorship
        
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
        "multiplier": multiplier
    }
    
    features.final_score = final
    return final, breakdown
