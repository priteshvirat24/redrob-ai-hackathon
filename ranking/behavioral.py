"""
Behavioral Scorer Agent.
Scores candidate availability, engagement, and logistics signals.
Implements JD rule: low response_rate + stale last_active = not available.
"""

from datetime import datetime
import logging
from config.types import Candidate, CandidateFeatures
from config.settings import (
    MIN_RESPONSE_RATE, GOOD_RESPONSE_RATE, MAX_INACTIVE_DAYS,
    MAX_NOTICE_PREFERRED, MAX_NOTICE_ACCEPTABLE, MIN_PROFILE_COMPLETENESS,
    REF_DATE,
)

logger = logging.getLogger(__name__)


def score_behavior(candidate: Candidate, features: CandidateFeatures) -> CandidateFeatures:
    """Calculate behavioral score from Redrob signals."""
    rs = candidate.redrob_signals

    # 1. Response Rate (Critical per JD)
    features.response_rate = rs.recruiter_response_rate
    resp_score = 0.0
    if features.response_rate >= GOOD_RESPONSE_RATE:
        resp_score = 1.0
    elif features.response_rate >= MIN_RESPONSE_RATE:
        resp_score = (features.response_rate - MIN_RESPONSE_RATE) / (GOOD_RESPONSE_RATE - MIN_RESPONSE_RATE)
    # Below MIN_RESPONSE_RATE gets 0

    # 2. Recency / Availability
    features.is_open_to_work = rs.open_to_work_flag

    # Calculate days since active using shared REF_DATE
    ref_dt = datetime(REF_DATE.year, REF_DATE.month, REF_DATE.day)
    try:
        last_active = datetime.strptime(rs.last_active_date, "%Y-%m-%d")
        features.days_since_active = (ref_dt - last_active).days
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
            notice_score = 0.5

    # 4. Profile Quality
    profile_score = rs.profile_completeness_score / 100.0
    if profile_score < (MIN_PROFILE_COMPLETENESS / 100.0):
        profile_score *= 0.5

    # 5. Github Activity (bonus for title_tier >= 2 so hidden gems get credit)
    features.github_score = rs.github_activity_score
    gh_bonus = 0.0
    if features.github_score > 0 and features.title_tier >= 2:
        gh_bonus = min(0.15, features.github_score / 250.0)

    # 6. Interview Reliability
    reliability = rs.interview_completion_rate

    # Combine into base behavioral score
    base = (
        (resp_score * 0.4) +
        (recency_score * 0.2) +
        (notice_score * 0.2) +
        (profile_score * 0.1) +
        (reliability * 0.1)
    )

    # Open-to-work: additive bonus capped at +0.05 (not multiplicative)
    if features.is_open_to_work:
        base = base + 0.05

    # JD availability penalty: low response + stale = not actually available
    if features.response_rate < MIN_RESPONSE_RATE and features.days_since_active > MAX_INACTIVE_DAYS:
        base *= 0.4

    features.behavioral_score = min(1.0, base + gh_bonus)

    return features
