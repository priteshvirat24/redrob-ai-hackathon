"""
Explainability Agent.
Generates the required reasoning string for each candidate in the top 100.
Pure Python, deterministic, no LLM, no network. Feature-driven with correct scale.
"""

from typing import List
from config.types import Candidate, CandidateFeatures, ScoredCandidate
from config.settings import (
    GOOD_RESPONSE_RATE, MIN_RESPONSE_RATE,
    MAX_NOTICE_PREFERRED, MAX_NOTICE_ACCEPTABLE,
    JD_ABSOLUTE_SKILLS, JD_PREFERRED_SKILLS,
    _normalize_skill,
)
from agents.base import BaseAgent

class ReasoningAgent(BaseAgent):
    def run(self, candidate_data: dict, scoring_details: dict) -> str:
        prompt = f"Candidate:\n{candidate_data}\n\nScoring Details:\n{scoring_details}"
        system = "You are an elite AI Recruiter. Generate a 2-3 sentence explanation of why this candidate was ranked highly, highlighting their strengths, weaknesses, and a suggested interview focus. Be professional and concise."
        return self.provider.chat_completion(system, prompt)


# Normalized lookup for matching
_ABS_NORM = {_normalize_skill(s) for s in JD_ABSOLUTE_SKILLS}
_PREF_NORM = {_normalize_skill(s) for s in JD_PREFERRED_SKILLS}


def _matched_skill_names(candidate: Candidate, limit: int = 3) -> List[str]:
    """Return up to `limit` real matched absolute/preferred skill names."""
    matched = []
    for s in candidate.skills:
        norm = _normalize_skill(s.name)
        if norm in _ABS_NORM or norm in _PREF_NORM:
            matched.append(s.name)
            if len(matched) >= limit:
                break
    return matched


def _response_phrase(rate: float) -> str:
    """Describe response rate using the correct config scale."""
    if rate >= GOOD_RESPONSE_RATE:
        return "responsive"
    if rate >= MIN_RESPONSE_RATE:
        return "moderately responsive"
    return "low responsiveness"


def _notice_phrase(days: int) -> str:
    """Describe notice period relative to config thresholds."""
    if days <= MAX_NOTICE_PREFERRED:
        return f"short {days}-day notice period"
    if days <= MAX_NOTICE_ACCEPTABLE:
        return f"{days}-day notice period"
    return f"long {days}-day notice period"


def _product_phrase(has_product: bool) -> str:
    if has_product:
        return "product company experience"
    return "no product company background"


def _specific_gap(features: CandidateFeatures) -> str:
    """Name the single most important gap for this candidate."""
    if features.is_non_tech_title:
        return f"non-technical title (tier {features.title_tier})"
    if features.has_consulting_only_career:
        return "consulting-only career background"
    if features.notice_period_days > MAX_NOTICE_ACCEPTABLE:
        return f"long notice period ({features.notice_period_days} days)"
    if features.response_rate < MIN_RESPONSE_RATE:
        return f"very low recruiter response rate ({features.response_rate:.2f})"
    if features.days_since_active > 180:
        return f"inactive for {features.days_since_active} days"
    if features.absolute_skill_count == 0:
        return "no matched absolute JD skills"
    if features.irrelevant_skill_ratio > 0.5:
        return f"high irrelevant skill ratio ({features.irrelevant_skill_ratio:.0%})"
    return "limited product company experience"


def generate_reasoning(candidate: Candidate, features: CandidateFeatures, rank: int, score: float) -> str:
    """
    Generate a specific, factual, deterministic reasoning string.
    Pure f-string composition from real feature values. No LLM, no templates chosen by rank%len.
    Always 2-3 complete sentences, always ends with a period, always <= 60 words.
    """
    p = candidate.profile
    title = p.current_title
    yoe = p.years_of_experience
    matched = _matched_skill_names(candidate)
    skills_str = ", ".join(matched) if matched else "general engineering"
    resp_phrase = _response_phrase(features.response_rate)
    notice_phrase = _notice_phrase(features.notice_period_days)
    product_phrase = _product_phrase(features.has_product_company_exp)

    if rank <= 25:
        # Strong candidates: lead with strengths
        sent1 = f"{title} with {yoe:.1f} years of experience and core skills in {skills_str}."
        sent2 = f"Demonstrates {product_phrase} and is {resp_phrase} with a {notice_phrase}."
    elif rank <= 60:
        # Mid-range: balanced strengths and gaps
        sent1 = f"{title} ({yoe:.1f} yrs) with relevant skills including {skills_str}."
        gap = _specific_gap(features)
        sent2 = f"Viable fit with {product_phrase}, though {gap} limits ranking."
    else:
        # Lower range: lead with gap
        gap = _specific_gap(features)
        sent1 = f"{title} with {yoe:.1f} years of experience, ranked lower due to {gap}."
        sent2 = f"Skills include {skills_str}; {resp_phrase} with {notice_phrase}."

    reasoning = f"{sent1} {sent2}"

    # Safety: ensure it ends with a period
    if not reasoning.strip().endswith("."):
        reasoning = reasoning.strip() + "."

    # Safety: truncate to 60 words max while keeping complete sentences
    words = reasoning.split()
    if len(words) > 58:
        # Find last period within 58 words
        truncated = " ".join(words[:58])
        last_period = truncated.rfind(".")
        if last_period > 0:
            reasoning = truncated[:last_period + 1]
        else:
            reasoning = truncated + "."

    return reasoning


# Blocklist for validation (no leaked prompts)
REASONING_BLOCKLIST = {
    "we need to produce",
    "2-3 sentence",
    "reasoning string",
    "you are an ai",
    "should be concise",
    "mention specific facts",
}


def validate_reasoning(reasoning: str, rank: int) -> str:
    """Validate reasoning and return a safe fallback if it fails checks."""
    text = reasoning.strip()
    lower = text.lower()

    # Check for leaked prompt text
    for blocked in REASONING_BLOCKLIST:
        if blocked in lower:
            return f"Candidate ranked #{rank} based on composite scoring of skills, experience, and availability signals."

    # Check it ends with a period
    if not text.endswith("."):
        text = text + "."

    # Check word count
    if len(text.split()) > 60:
        text = " ".join(text.split()[:55]) + "."

    # Check non-empty
    if len(text) < 10:
        return f"Candidate ranked #{rank} based on composite scoring of skills, experience, and availability signals."

    return text
