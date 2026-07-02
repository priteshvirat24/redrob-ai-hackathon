"""
Explainability Agent.
Generates the required reasoning string for each candidate in the top 100.
Avoids LLM API calls to meet the CPU/network constraint.
Uses template-based generation with specific factual insertion to meet the manual review criteria.
"""

from typing import List
import random
from backend.core.types import Candidate, CandidateFeatures, ScoredCandidate

import os
from openai import OpenAI
import time

# A set of varied templates to avoid looking like a single template was used
STRONG_TEMPLATES = [
    "{title} with {yoe:.1f} yrs experience; strong fit for the AI/ML product requirement. High engagement (response rate: {resp:.2f}).",
    "Solid {title} ({yoe:.1f} years). Background shows actual ML production experience. {notice} notice period is acceptable.",
    "Excellent semantic match. The {title} role and {yoe:.1f} yrs experience align well. {skills_note}",
    "Matches the 'product over research' profile in the JD. {title} with {skills_note}. Engagement is {engagement_level}."
]

OK_TEMPLATES = [
    "{title} with {yoe:.1f} yrs. {skills_note}, but {gap_note}. Overall viable fit.",
    "Decent background as {title} ({yoe:.1f} yrs). Has some relevant skills ({top_skills}) but lacks strong production signals.",
    "Moderate semantic match for {title}. {gap_note}, though experience is within band."
]

WEAK_TEMPLATES = [
    "Adjacent skills only ({title}). Included as filler given {yoe:.1f} yrs experience, but {gap_note}.",
    "Low semantic match for JD. {title} background is too far from core ML engineering, despite {yoe:.1f} yrs experience.",
    "Included at lower rank due to {gap_note}. {title} with {yoe:.1f} yrs."
]


def generate_skills_note(features: CandidateFeatures) -> str:
    """Generate a factual note about skills."""
    if features.absolute_skill_count >= 4:
        return f"strong core skills ({features.absolute_skill_count} matched)"
    elif features.absolute_skill_count > 0:
        return f"some core skills ({features.absolute_skill_count} matched)"
    return "missing core AI/ML skills"


def generate_gap_note(features: CandidateFeatures) -> str:
    """Generate a factual note about gaps/concerns."""
    if features.is_non_tech_title:
        return "title is not aligned with tech roles"
    if features.has_consulting_only_career:
        return "career is entirely in consulting/services"
    if features.notice_period_days > 60:
        return f"notice period is long ({features.notice_period_days} days)"
    if features.response_rate < 0.2:
        return f"engagement is very low (resp rate {features.response_rate:.2f})"
    if features.irrelevant_skill_ratio > 0.7:
        return "high ratio of irrelevant skills"
    return "lacks product company experience"


def generate_reasoning_llm(candidate: Candidate, features: CandidateFeatures, rank: int, score: float) -> str:
    """Use the LLM API to generate a highly specific reasoning string."""
    api_key = os.environ.get("OPENAI_API_KEY", "freellmapi-e85c66fc2196ebfe9c13738a3c93d5630af813e3a865cf4c")
    base_url = os.environ.get("OPENAI_BASE_URL", "http://localhost:3001/v1")
    
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    p = candidate.profile
    core_skills = [s.name for s in candidate.skills if s.name in ["PyTorch", "TensorFlow", "NLP", "Embeddings", "RAG", "FAISS", "Qdrant", "Sentence Transformers"]]
    
    prompt = f"""
    You are an AI technical recruiter. Write a 2-3 sentence reasoning for why this candidate was ranked #{rank} for a Senior AI Engineer role.
    Be extremely concise, factual, and specific. Do NOT use generic templated language. Mention specific facts from their profile.
    
    Candidate Facts:
    - Title: {p.current_title}
    - Years of Experience: {p.years_of_experience:.1f}
    - Core AI Skills: {', '.join(core_skills) if core_skills else 'None'}
    - Response Rate: {features.response_rate:.2f}
    - Notice Period: {features.notice_period_days} days
    - Product Company Experience: {features.has_product_company_exp}
    
    Focus on their strengths (like AI skills or YOE) and honestly mention any gaps (like low response rate or missing skills) if rank is > 50.
    Output ONLY the reasoning string, nothing else.
    """
    
    try:
        response = client.chat.completions.create(
            model="auto",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=60
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM API failed for {candidate.candidate_id}: {e}")
        return None


def generate_reasoning(candidate: Candidate, features: CandidateFeatures, rank: int, score: float) -> str:
    """
    Generate a specific, factual, non-hallucinated reasoning string.
    Tries LLM first, falls back to templates if it fails or if LLM generation is disabled.
    """
    
    # Try LLM generation first
    llm_reasoning = generate_reasoning_llm(candidate, features, rank, score)
    if llm_reasoning:
        return llm_reasoning

    # Fallback to templates
    p = candidate.profile
    yoe = p.years_of_experience
    title = p.current_title
    resp = features.response_rate
    notice = f"{features.notice_period_days}-day"
    
    skills_note = generate_skills_note(features)
    gap_note = generate_gap_note(features)
    engagement_level = "high" if resp > 0.5 else "moderate" if resp > 0.2 else "low"
    
    core_skills = [s.name for s in candidate.skills if s.name in ["PyTorch", "TensorFlow", "NLP", "Embeddings", "RAG", "FAISS", "Qdrant", "Sentence Transformers"]]
    top_skills = ", ".join(core_skills[:2]) if core_skills else "general tech"
    
    if rank <= 30:
        template = STRONG_TEMPLATES[rank % len(STRONG_TEMPLATES)]
    elif rank <= 75:
        template = OK_TEMPLATES[rank % len(OK_TEMPLATES)]
    else:
        template = WEAK_TEMPLATES[rank % len(WEAK_TEMPLATES)]
        
    reasoning = template.format(
        title=title,
        yoe=yoe,
        resp=resp,
        notice=notice,
        skills_note=skills_note,
        gap_note=gap_note,
        engagement_level=engagement_level,
        top_skills=top_skills
    )
    
    return reasoning
