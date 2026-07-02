"""
Behavioral Scorer Agent.
Scores candidate availability, engagement, and logistics signals.
"""

from datetime import datetime
import logging
from backend.core.types import Candidate, CandidateFeatures
from backend.core.config import (
    MIN_RESPONSE_RATE, GOOD_RESPONSE_RATE, MAX_INACTIVE_DAYS,
    MAX_NOTICE_PREFERRED, MAX_NOTICE_ACCEPTABLE, MIN_PROFILE_COMPLETENESS
)

logger = logging.getLogger(__name__)


def score_behavior(candidate: Candidate, features: CandidateFeatures) -> CandidateFeatures:
    """Calculate behavioral multiplier from Redrob signals."""
    rs = candidate.redrob_signals
    
    # 1. Response Rate (Critical)
    features.response_rate = rs.recruiter_response_rate
    resp_score = 0.0
    if features.response_rate >= GOOD_RESPONSE_RATE:
        resp_score = 1.0
    elif features.response_rate >= MIN_RESPONSE_RATE:
        resp_score = (features.response_rate - MIN_RESPONSE_RATE) / (GOOD_RESPONSE_RATE - MIN_RESPONSE_RATE)
    # Below MIN_RESPONSE_RATE gets 0
        
    # 2. Recency / Availability
    features.is_open_to_work = rs.open_to_work_flag
    
    # Calculate days since active (relative to dataset reference date roughly May 2026)
    ref_date = datetime(2026, 5, 30)
    try:
        last_active = datetime.strptime(rs.last_active_date, "%Y-%m-%d")
        features.days_since_active = (ref_date - last_active).days
    except ValueError:
        features.days_since_active = 999
        
    recency_score = 1.0
    if features.days_since_active > MAX_INACTIVE_DAYS:
        recency_score = max(0.0, 1.0 - ((features.days_since_active - MAX_INACTIVE_DAYS) / 180.0))
        
    # 3. Logistics (Notice Period)
    features.notice_period_days = rs.notice_period_days
    notice_score = 1.0
    if features.notice_period_days > MAX_NOTICE_PREFERRED:
        if features.notice_period_days <= MAX_NOTICE_ACCEPTABLE:
            notice_score = 0.8
        else:
            notice_score = 0.5 # Long notice period penalty
            
    # 4. Profile Quality
    profile_score = rs.profile_completeness_score / 100.0
    if profile_score < (MIN_PROFILE_COMPLETENESS / 100.0):
        profile_score *= 0.5 # Penalty for very incomplete profiles
        
    # 5. Github Activity (Bonus for tech roles)
    features.github_score = rs.github_activity_score
    gh_bonus = 0.0
    if features.github_score > 0 and features.title_tier >= 3:
        gh_bonus = min(0.2, features.github_score / 200.0)
        
    # 6. Interview Reliability
    reliability = rs.interview_completion_rate
        
    # Combine into final behavioral score (max 1.0, though gh_bonus can push slightly higher)
    base = (resp_score * 0.4) + (recency_score * 0.2) + (notice_score * 0.2) + (profile_score * 0.1) + (reliability * 0.1)
    
    # Apply open-to-work multiplier
    if features.is_open_to_work:
        base = min(1.0, base * 1.2)
        
    features.behavioral_score = min(1.0, base + gh_bonus)
    
    return features
