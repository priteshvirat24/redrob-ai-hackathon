"""
Skill Graph Agent.
Analyzes skill match between candidate and JD with normalized matching.
"""

from typing import List, Dict
import logging
from config.types import Candidate, CandidateFeatures
from config.settings import (
    JD_ABSOLUTE_SKILLS_NORM, JD_PREFERRED_SKILLS_NORM, JD_IRRELEVANT_SKILLS_NORM,
    _normalize_skill, SKILL_ALIASES,
)

logger = logging.getLogger(__name__)


def proficiency_weight(prof: str) -> float:
    weights = {
        "expert": 1.0,
        "advanced": 0.8,
        "intermediate": 0.5,
        "beginner": 0.2
    }
    return weights.get(prof, 0.1)


def normalize_and_alias(name: str) -> str:
    """Normalize skill name and resolve aliases."""
    norm = _normalize_skill(name)
    return SKILL_ALIASES.get(norm, norm)


def score_skills(candidate: Candidate, features: CandidateFeatures) -> CandidateFeatures:
    """Calculate skill match scores based on JD requirements with normalized matching."""

    abs_score = 0.0
    pref_score = 0.0
    irr_count = 0
    total_skills = len(candidate.skills)

    features.absolute_skill_count = 0
    features.preferred_skill_count = 0

    # Track assessment verification
    verified_bonus = 0.0
    assessments = candidate.redrob_signals.skill_assessment_scores

    # Track matched skill names for reasoning
    matched_absolute_names = []
    matched_preferred_names = []

    for skill in candidate.skills:
        name_raw = skill.name
        name_norm = normalize_and_alias(name_raw)
        prof_wt = proficiency_weight(skill.proficiency)

        # Duration multiplier (up to 1.5x for long duration, penalize 0 duration)
        dur_wt = 0.1 if skill.duration_months == 0 else min(1.5, 0.5 + (skill.duration_months / 24))

        # Endorsement multiplier (up to 1.2x)
        end_wt = min(1.2, 1.0 + (skill.endorsements / 50))

        # Verification bonus
        verif_wt = 1.0
        if name_raw in assessments:
            score_val = assessments[name_raw]
            if score_val > 80:
                verif_wt = 1.5
                verified_bonus += 0.1
            elif score_val > 60:
                verif_wt = 1.2
            else:
                verif_wt = 0.8

        base_score = prof_wt * dur_wt * end_wt * verif_wt

        if name_norm in JD_ABSOLUTE_SKILLS_NORM:
            abs_score += base_score
            features.absolute_skill_count += 1
            matched_absolute_names.append(name_raw)
        elif name_norm in JD_PREFERRED_SKILLS_NORM:
            pref_score += base_score * 0.5
            features.preferred_skill_count += 1
            matched_preferred_names.append(name_raw)
        elif name_norm in JD_IRRELEVANT_SKILLS_NORM:
            irr_count += 1

    # Calculate final skill scores
    if total_skills > 0:
        features.irrelevant_skill_ratio = irr_count / total_skills

    features.verified_skill_score = verified_bonus

    # Normalize with a higher max_expected to prevent saturation
    # so strong candidates land in ~0.6-0.9 not pinned at 1.0
    max_expected = len(JD_ABSOLUTE_SKILLS_NORM) * 2.0 + len(JD_PREFERRED_SKILLS_NORM) * 1.0
    raw_total = abs_score + pref_score

    features.skill_match_score = min(1.0, raw_total / max_expected)

    return features
