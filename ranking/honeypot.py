"""
Honeypot Detector Agent.
Identifies trap candidates in the dataset (impossible profiles, keyword stuffers).
Returns a graded honeypot_score in [0,1] in addition to the boolean flag.
"""

from typing import List, Tuple
from datetime import datetime
import logging
from config.types import Candidate, CandidateFeatures
from config.settings import (
    NON_TECH_TITLES, JD_ABSOLUTE_SKILLS, JD_PREFERRED_SKILLS,
    REF_DATE, _normalize_skill,
)

logger = logging.getLogger(__name__)

# Combine core AI skills (normalized for matching)
AI_CORE_SKILLS_NORM = {_normalize_skill(s) for s in (JD_ABSOLUTE_SKILLS | JD_PREFERRED_SKILLS)}


def check_duration_mismatch(candidate: Candidate) -> List[str]:
    """Check if the stated duration matches the start/end dates."""
    flags = []
    ref_dt = datetime(REF_DATE.year, REF_DATE.month, REF_DATE.day)

    for job in candidate.career_history:
        start = job.start_date
        end = job.end_date
        dur = job.duration_months

        if not start or not dur:
            continue

        try:
            s_date = datetime.strptime(start, "%Y-%m-%d")
            e_date = datetime.strptime(end, "%Y-%m-%d") if end else ref_dt

            actual_months = (e_date.year - s_date.year) * 12 + (e_date.month - s_date.month)

            # If discrepancy is > 12 months, it is a huge red flag
            if abs(actual_months - dur) > 12:
                flags.append(f"Job at {job.company}: stated {dur}mo but dates span {actual_months}mo")
        except ValueError:
            pass

    return flags


def check_impossible_skills(candidate: Candidate) -> List[str]:
    """Check for expert proficiency with 0 months duration. Threshold >= 2."""
    flags = []
    expert_zero = [
        s.name for s in candidate.skills
        if s.proficiency == "expert" and s.duration_months == 0
    ]

    # >= 2 expert skills with 0 months is a honeypot signal
    if len(expert_zero) >= 2:
        flags.append(f"{len(expert_zero)} expert skills with 0 months duration: {', '.join(expert_zero[:4])}")

    return flags


def check_keyword_stuffing(candidate: Candidate, title_tier: int) -> List[str]:
    """Check for non-tech/low-tier titles overloaded with AI keywords."""
    flags = []

    # Fire when title_tier <= 1 AND ai_skill_count >= 5 (not just exact NON_TECH match)
    if title_tier <= 1:
        ai_skill_count = sum(
            1 for s in candidate.skills
            if _normalize_skill(s.name) in AI_CORE_SKILLS_NORM
        )
        if ai_skill_count >= 5:
            title = candidate.profile.current_title
            flags.append(f"Low-tier title '{title}' (tier {title_tier}) with {ai_skill_count} AI core skills")

    return flags


def run_honeypot_detector(candidate: Candidate, features: CandidateFeatures) -> CandidateFeatures:
    """Run all honeypot checks and update features with graded score."""
    flags = []

    flags.extend(check_duration_mismatch(candidate))
    flags.extend(check_impossible_skills(candidate))
    flags.extend(check_keyword_stuffing(candidate, features.title_tier))

    if flags:
        features.is_honeypot = True
        features.honeypot_flags = flags

    # Graded score: 0.0 = clean, 1.0 = definite honeypot
    # Each flag adds 0.4 to the score (capped at 1.0)
    features.honeypot_score = min(1.0, len(flags) * 0.4)

    return features
