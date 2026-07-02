"""
Candidate Profiler Agent.
Extracts basic features from the candidate profile (title relevance, experience, career coherence).
"""

from datetime import datetime
import logging
from backend.core.types import Candidate, CandidateFeatures
from backend.core.config import (
    TIER5_TITLES, TIER4_TITLES, TIER3_TITLES, NON_TECH_TITLES,
    CONSULTING_COMPANIES, PRODUCT_INDUSTRIES,
    IDEAL_YOE_MIN, IDEAL_YOE_MAX, ACCEPTABLE_YOE_MIN, ACCEPTABLE_YOE_MAX,
    PREFERRED_LOCATIONS, PREFERRED_COUNTRY
)

logger = logging.getLogger(__name__)


def classify_title(title: str) -> int:
    """Score title relevance from 1-5."""
    if title in TIER5_TITLES:
        return 5
    if title in TIER4_TITLES:
        return 4
    if title in TIER3_TITLES:
        return 3
    if title in NON_TECH_TITLES:
        return 1
    # Unknown tech titles fall into 2
    if any(t in title.lower() for t in ['engineer', 'developer', 'scientist', 'architect', 'analyst']):
        return 2
    return 1


def calculate_experience_score(yoe: float) -> float:
    """Score experience based on JD preference (5-9 years)."""
    if IDEAL_YOE_MIN <= yoe <= IDEAL_YOE_MAX:
        return 1.0
    if ACCEPTABLE_YOE_MIN <= yoe < IDEAL_YOE_MIN:
        # 3-5 years: partial credit
        return 0.7 * ((yoe - ACCEPTABLE_YOE_MIN) / (IDEAL_YOE_MIN - ACCEPTABLE_YOE_MIN) + 0.1)
    if IDEAL_YOE_MAX < yoe <= ACCEPTABLE_YOE_MAX:
        # 9-14 years: partial credit, decaying
        return 0.8 * (1.0 - (yoe - IDEAL_YOE_MAX) / (ACCEPTABLE_YOE_MAX - IDEAL_YOE_MAX + 1))
    return 0.0


def analyze_career_history(candidate: Candidate, features: CandidateFeatures) -> CandidateFeatures:
    """Analyze career progression, company types, and job hopping."""
    history = candidate.career_history
    features.career_job_count = len(history)
    
    if features.career_job_count > 0:
        total_months = sum(j.duration_months for j in history)
        features.avg_tenure_months = total_months / features.career_job_count
        
        # Check for consulting-only career
        # If ALL jobs are at consulting companies, that's a red flag per JD
        consulting_jobs = sum(1 for j in history if j.company in CONSULTING_COMPANIES)
        features.has_consulting_only_career = (consulting_jobs == features.career_job_count)
        
        # Check for product company experience
        features.has_product_company_exp = any(j.industry in PRODUCT_INDUSTRIES for j in history)
        
        # Title chaser detection: high job count + low tenure
        if features.career_job_count >= 4 and features.avg_tenure_months < 18:
            features.is_title_chaser = True
            
        # Career progression: simple check if title changes
        titles = [j.title for j in history]
        unique_titles = len(set(titles))
        if unique_titles > 1 and features.avg_tenure_months > 18:
            features.career_progression_score = min(1.0, unique_titles * 0.25)
    
    return features


def analyze_location(candidate: Candidate, features: CandidateFeatures) -> CandidateFeatures:
    """Score location fit."""
    p = candidate.profile
    features.is_india = (p.country == PREFERRED_COUNTRY)
    
    if not features.is_india:
        features.location_score = 0.0
    else:
        # In India, check if in preferred city
        if any(loc in p.location for loc in PREFERRED_LOCATIONS):
            features.location_score = 1.0
        else:
            features.location_score = 0.5 # India but not preferred city
            
    return features


def build_text_for_embedding(candidate: Candidate, features: CandidateFeatures) -> CandidateFeatures:
    """Concatenate career descriptions for semantic search."""
    p = candidate.profile
    
    # Profile text: headline + summary
    features.profile_text = f"{p.headline}. {p.summary}"
    
    # Career text: all descriptions
    career_texts = []
    for job in candidate.career_history:
        career_texts.append(f"Role: {job.title} at {job.company} ({job.industry}). {job.description}")
        
    features.career_text = " ".join(career_texts)
    
    return features


def run_profiler(candidate: Candidate) -> CandidateFeatures:
    """Run all basic profiling checks and initialize features."""
    features = CandidateFeatures(candidate_id=candidate.candidate_id)
    p = candidate.profile
    
    features.title_tier = classify_title(p.current_title)
    features.is_non_tech_title = (features.title_tier == 1)
    
    features.years_of_experience = p.years_of_experience
    features.experience_fit_score = calculate_experience_score(p.years_of_experience)
    
    features = analyze_career_history(candidate, features)
    features = analyze_location(candidate, features)
    features = build_text_for_embedding(candidate, features)
    
    # Basic education check
    if candidate.education:
        tiers = [e.tier for e in candidate.education]
        if "tier_1" in tiers:
            features.best_tier = "tier_1"
            features.education_score = 1.0
        elif "tier_2" in tiers:
            features.best_tier = "tier_2"
            features.education_score = 0.7
        elif "tier_3" in tiers:
            features.best_tier = "tier_3"
            features.education_score = 0.3
        else:
            features.best_tier = "tier_4"
            features.education_score = 0.1
            
    return features
