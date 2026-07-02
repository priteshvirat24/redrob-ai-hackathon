"""
Skill Graph Agent.
Analyzes skill match between candidate and JD.
"""

from typing import List, Dict
import logging
from backend.core.types import Candidate, CandidateFeatures
from backend.core.config import JD_ABSOLUTE_SKILLS, JD_PREFERRED_SKILLS, JD_IRRELEVANT_SKILLS

logger = logging.getLogger(__name__)


def proficiency_weight(prof: str) -> float:
    weights = {
        "expert": 1.0,
        "advanced": 0.8,
        "intermediate": 0.5,
        "beginner": 0.2
    }
    return weights.get(prof, 0.1)


def score_skills(candidate: Candidate, features: CandidateFeatures) -> CandidateFeatures:
    """Calculate skill match scores based on JD requirements."""
    
    abs_score = 0.0
    pref_score = 0.0
    irr_count = 0
    total_skills = len(candidate.skills)
    
    features.absolute_skill_count = 0
    features.preferred_skill_count = 0
    
    # Track assessment verification
    verified_bonus = 0.0
    assessments = candidate.redrob_signals.skill_assessment_scores
    
    for skill in candidate.skills:
        name = skill.name
        prof_wt = proficiency_weight(skill.proficiency)
        
        # Duration multiplier (up to 1.5x for long duration, penalize 0 duration)
        dur_wt = 0.1 if skill.duration_months == 0 else min(1.5, 0.5 + (skill.duration_months / 24))
        
        # Endorsement multiplier (up to 1.2x)
        end_wt = min(1.2, 1.0 + (skill.endorsements / 50))
        
        # Verification bonus
        verif_wt = 1.0
        if name in assessments:
            score = assessments[name]
            if score > 80:
                verif_wt = 1.5
                verified_bonus += 0.1
            elif score > 60:
                verif_wt = 1.2
            else:
                verif_wt = 0.8 # Failed assessment penalty
        
        base_score = prof_wt * dur_wt * end_wt * verif_wt
        
        if name in JD_ABSOLUTE_SKILLS:
            abs_score += base_score
            features.absolute_skill_count += 1
        elif name in JD_PREFERRED_SKILLS:
            pref_score += base_score * 0.5 # Preferred skills worth half
            features.preferred_skill_count += 1
        elif name in JD_IRRELEVANT_SKILLS:
            irr_count += 1
            
    # Calculate final skill scores
    if total_skills > 0:
        features.irrelevant_skill_ratio = irr_count / total_skills
    
    features.verified_skill_score = verified_bonus
    
    # Normalize (approx max achievable is ~15 for absolute + ~10 for preferred)
    max_expected = len(JD_ABSOLUTE_SKILLS) * 1.5 + len(JD_PREFERRED_SKILLS) * 0.75
    raw_total = abs_score + pref_score
    
    features.skill_match_score = min(1.0, raw_total / max_expected)
    
    return features
