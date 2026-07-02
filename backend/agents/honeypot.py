"""
Honeypot Detector Agent.
Identifies trap candidates in the dataset (impossible profiles, keyword stuffers).
"""

from typing import List, Tuple
from datetime import datetime
import logging
from backend.core.types import Candidate, CandidateFeatures
from backend.core.config import NON_TECH_TITLES, JD_ABSOLUTE_SKILLS, JD_PREFERRED_SKILLS

logger = logging.getLogger(__name__)

# Combine core AI skills
AI_CORE_SKILLS = JD_ABSOLUTE_SKILLS | JD_PREFERRED_SKILLS


def check_duration_mismatch(candidate: Candidate) -> List[str]:
    """Check if the stated duration matches the start/end dates."""
    flags = []
    for job in candidate.career_history:
        start = job.start_date
        end = job.end_date
        dur = job.duration_months
        
        if not start or not dur:
            continue
            
        try:
            s_date = datetime.strptime(start, "%Y-%m-%d")
            # If no end date, assume they are still working there (use a reasonable recent date for hackathon dataset context like May 2026)
            e_date = datetime.strptime(end, "%Y-%m-%d") if end else datetime(2026, 5, 1)
            
            actual_months = (e_date.year - s_date.year) * 12 + (e_date.month - s_date.month)
            
            # If discrepancy is > 12 months, it's a huge red flag
            if abs(actual_months - dur) > 12:
                flags.append(f"Job at {job.company}: stated {dur}mo but dates span {actual_months}mo")
        except ValueError:
            pass
            
    return flags


def check_impossible_skills(candidate: Candidate) -> List[str]:
    """Check for expert proficiency with 0 months duration."""
    flags = []
    expert_zero = [s.name for s in candidate.skills if s.proficiency == 'expert' and s.duration_months == 0]
    
    # 1 or 2 might be a data entry error, >= 3 is definitely a honeypot
    if len(expert_zero) >= 3:
        flags.append(f"{len(expert_zero)} expert skills with 0 months duration")
        
    return flags


def check_keyword_stuffing(candidate: Candidate) -> List[str]:
    """Check for non-tech titles overloaded with AI keywords."""
    flags = []
    title = candidate.profile.current_title
    
    if title in NON_TECH_TITLES:
        ai_skill_count = sum(1 for s in candidate.skills if s.name in AI_CORE_SKILLS)
        if ai_skill_count >= 5:
            flags.append(f"Non-tech title '{title}' with {ai_skill_count} AI core skills")
            
    return flags


def run_honeypot_detector(candidate: Candidate, features: CandidateFeatures) -> CandidateFeatures:
    """Run all honeypot checks and update features."""
    flags = []
    
    flags.extend(check_duration_mismatch(candidate))
    flags.extend(check_impossible_skills(candidate))
    flags.extend(check_keyword_stuffing(candidate))
    
    if flags:
        features.is_honeypot = True
        features.honeypot_flags = flags
        
    return features
