"""
Core data types for the AI Recruiting Copilot.
Pydantic models for candidates, features, and scoring results.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import date


@dataclass
class Profile:
    anonymized_name: str
    headline: str
    summary: str
    location: str
    country: str
    years_of_experience: float
    current_title: str
    current_company: str
    current_company_size: str
    current_industry: str


@dataclass
class CareerEntry:
    company: str
    title: str
    start_date: str
    end_date: Optional[str]
    duration_months: int
    is_current: bool
    industry: str
    company_size: str
    description: str


@dataclass
class Education:
    institution: str
    degree: str
    field_of_study: str
    start_year: int
    end_year: int
    grade: Optional[str] = None
    tier: str = "unknown"


@dataclass
class Skill:
    name: str
    proficiency: str
    endorsements: int
    duration_months: int = 0


@dataclass
class Certification:
    name: str
    issuer: str
    year: int


@dataclass
class Language:
    language: str
    proficiency: str


@dataclass
class SalaryRange:
    min: float
    max: float


@dataclass
class RedrobSignals:
    profile_completeness_score: float
    signup_date: str
    last_active_date: str
    open_to_work_flag: bool
    profile_views_received_30d: int
    applications_submitted_30d: int
    recruiter_response_rate: float
    avg_response_time_hours: float
    skill_assessment_scores: Dict[str, float]
    connection_count: int
    endorsements_received: int
    notice_period_days: int
    expected_salary_range_inr_lpa: SalaryRange
    preferred_work_mode: str
    willing_to_relocate: bool
    github_activity_score: float
    search_appearance_30d: int
    saved_by_recruiters_30d: int
    interview_completion_rate: float
    offer_acceptance_rate: float
    verified_email: bool
    verified_phone: bool
    linkedin_connected: bool


@dataclass
class Candidate:
    """Full candidate record from the dataset."""
    candidate_id: str
    profile: Profile
    career_history: List[CareerEntry]
    education: List[Education]
    skills: List[Skill]
    certifications: List[Certification]
    languages: List[Language]
    redrob_signals: RedrobSignals

    @classmethod
    def from_dict(cls, data: dict) -> "Candidate":
        """Parse a raw JSON dict into a structured Candidate."""
        p = data["profile"]
        profile = Profile(**p)

        career = [CareerEntry(**c) for c in data.get("career_history", [])]

        education = [
            Education(
                institution=e["institution"],
                degree=e["degree"],
                field_of_study=e["field_of_study"],
                start_year=e["start_year"],
                end_year=e["end_year"],
                grade=e.get("grade"),
                tier=e.get("tier", "unknown"),
            )
            for e in data.get("education", [])
        ]

        skills = [
            Skill(
                name=s["name"],
                proficiency=s["proficiency"],
                endorsements=s["endorsements"],
                duration_months=s.get("duration_months", 0),
            )
            for s in data.get("skills", [])
        ]

        certs = [Certification(**c) for c in data.get("certifications", [])]
        langs = [Language(**l) for l in data.get("languages", [])]

        rs = data["redrob_signals"]
        sal = rs["expected_salary_range_inr_lpa"]
        signals = RedrobSignals(
            profile_completeness_score=rs["profile_completeness_score"],
            signup_date=rs["signup_date"],
            last_active_date=rs["last_active_date"],
            open_to_work_flag=rs["open_to_work_flag"],
            profile_views_received_30d=rs["profile_views_received_30d"],
            applications_submitted_30d=rs["applications_submitted_30d"],
            recruiter_response_rate=rs["recruiter_response_rate"],
            avg_response_time_hours=rs["avg_response_time_hours"],
            skill_assessment_scores=rs.get("skill_assessment_scores", {}),
            connection_count=rs["connection_count"],
            endorsements_received=rs["endorsements_received"],
            notice_period_days=rs["notice_period_days"],
            expected_salary_range_inr_lpa=SalaryRange(min=sal["min"], max=sal["max"]),
            preferred_work_mode=rs["preferred_work_mode"],
            willing_to_relocate=rs["willing_to_relocate"],
            github_activity_score=rs["github_activity_score"],
            search_appearance_30d=rs["search_appearance_30d"],
            saved_by_recruiters_30d=rs["saved_by_recruiters_30d"],
            interview_completion_rate=rs["interview_completion_rate"],
            offer_acceptance_rate=rs["offer_acceptance_rate"],
            verified_email=rs["verified_email"],
            verified_phone=rs["verified_phone"],
            linkedin_connected=rs["linkedin_connected"],
        )

        return cls(
            candidate_id=data["candidate_id"],
            profile=profile,
            career_history=career,
            education=education,
            skills=skills,
            certifications=certs,
            languages=langs,
            redrob_signals=signals,
        )


@dataclass
class CandidateFeatures:
    """Pre-computed features for a single candidate."""
    candidate_id: str

    # Title & role classification
    title_tier: int = 0              # 5=perfect, 4=strong, 3=tech, 2=adjacent, 1=non-tech, 0=disqualified
    is_non_tech_title: bool = False

    # Honeypot detection
    is_honeypot: bool = False
    honeypot_flags: List[str] = field(default_factory=list)

    # Career analysis
    has_consulting_only_career: bool = False
    has_product_company_exp: bool = False
    career_job_count: int = 0
    avg_tenure_months: float = 0.0
    is_title_chaser: bool = False
    career_progression_score: float = 0.0

    # Skill matching
    absolute_skill_count: int = 0
    preferred_skill_count: int = 0
    irrelevant_skill_ratio: float = 0.0
    verified_skill_score: float = 0.0
    skill_match_score: float = 0.0

    # Experience
    years_of_experience: float = 0.0
    experience_fit_score: float = 0.0

    # Education
    education_score: float = 0.0
    best_tier: str = "unknown"

    # Location
    location_score: float = 0.0
    is_india: bool = False

    # Behavioral signals
    behavioral_score: float = 0.0
    response_rate: float = 0.0
    days_since_active: int = 999
    notice_period_days: int = 0
    github_score: float = -1.0
    is_open_to_work: bool = False

    # Semantic (populated during embedding phase)
    semantic_score: float = 0.0

    # Composite
    final_score: float = 0.0

    # Text for embedding
    career_text: str = ""
    profile_text: str = ""


@dataclass
class ScoredCandidate:
    """A fully scored candidate ready for ranking."""
    candidate_id: str
    rank: int
    score: float
    reasoning: str
    features: CandidateFeatures

    # Score breakdown for explainability
    score_breakdown: Dict[str, float] = field(default_factory=dict)
