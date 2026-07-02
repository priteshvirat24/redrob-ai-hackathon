"""
Core configuration for the AI Recruiting Copilot.
Centralizes all paths, weights, thresholds, and model settings.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict


# ── Paths ─────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATASET_DIR = PROJECT_ROOT / "[PUB] India_runs_data_and_ai_challenge" / "India_runs_data_and_ai_challenge"
CANDIDATES_FILE = DATASET_DIR / "candidates.jsonl"
JD_FILE = DATASET_DIR / "job_description.txt"
PRECOMPUTED_DIR = PROJECT_ROOT / "backend" / "precomputed"

# Ensure precomputed dir exists
PRECOMPUTED_DIR.mkdir(parents=True, exist_ok=True)


# ── Scoring Weights ──────────────────────────────────────────────────
@dataclass
class ScoringWeights:
    """Configurable weights for the composite ranking score."""
    semantic_match: float = 0.30
    title_relevance: float = 0.25
    skill_match: float = 0.15
    experience_fit: float = 0.10
    career_coherence: float = 0.10
    education: float = 0.05
    behavioral: float = 0.05

    def as_dict(self) -> Dict[str, float]:
        return {
            "semantic_match": self.semantic_match,
            "title_relevance": self.title_relevance,
            "skill_match": self.skill_match,
            "experience_fit": self.experience_fit,
            "career_coherence": self.career_coherence,
            "education": self.education,
            "behavioral": self.behavioral,
        }


# ── Title Categories ─────────────────────────────────────────────────
# Tier 5: Perfect AI/ML title match for the JD
TIER5_TITLES = {
    "AI Engineer", "ML Engineer", "Machine Learning Engineer",
    "Applied ML Engineer", "Senior Software Engineer (ML)",
    "Search Engineer", "Recommendation Systems Engineer",
    "Senior Data Scientist", "AI Research Engineer",
}

# Tier 4: Strong data/ML adjacent titles
TIER4_TITLES = {
    "Data Scientist", "Data Engineer", "Senior Data Engineer",
    "Analytics Engineer", "Computer Vision Engineer",
    "Junior ML Engineer", "AI Specialist", "Backend Engineer",
}

# Tier 3: General tech titles with potential
TIER3_TITLES = {
    "Software Engineer", "Senior Software Engineer",
    "Full Stack Developer", "Cloud Engineer", "DevOps Engineer",
    "Java Developer", ".NET Developer", "Data Analyst",
    "Frontend Engineer", "QA Engineer", "Mobile Developer",
}

# Tier 1-2: Non-tech titles (traps if they have AI keywords)
NON_TECH_TITLES = {
    "Marketing Manager", "HR Manager", "Accountant", "Sales Executive",
    "Customer Support", "Content Writer", "Graphic Designer",
    "Operations Manager", "Civil Engineer", "Mechanical Engineer",
    "Project Manager", "Business Analyst",
}


# ── JD Disqualifiers ─────────────────────────────────────────────────
CONSULTING_COMPANIES = {
    "TCS", "Infosys", "Wipro", "Accenture", "Cognizant", "Capgemini",
    "Tech Mahindra", "HCL Technologies", "Mindtree", "Mphasis",
    "L&T Infotech", "KPMG", "Deloitte", "PwC", "EY",
}

# Product company industries (positive signal)
PRODUCT_INDUSTRIES = {
    "Software", "Fintech", "E-commerce", "Food Delivery",
    "SaaS", "AI/ML", "Consumer Tech", "Health Tech",
}

# Services / non-relevant industries
SERVICES_INDUSTRIES = {
    "IT Services", "Consulting", "BPO", "Staffing",
}


# ── Experience Band ──────────────────────────────────────────────────
IDEAL_YOE_MIN = 5.0
IDEAL_YOE_MAX = 9.0
ACCEPTABLE_YOE_MIN = 3.0
ACCEPTABLE_YOE_MAX = 14.0


# ── Location ─────────────────────────────────────────────────────────
PREFERRED_LOCATIONS = {
    "Pune", "Noida", "Hyderabad", "Mumbai", "Delhi", "Delhi NCR",
    "Gurgaon", "Gurugram", "Bangalore", "Bengaluru", "Chennai",
    "Pune, Maharashtra", "Noida, Uttar Pradesh",
}

PREFERRED_COUNTRY = "India"


# ── Behavioral Thresholds ────────────────────────────────────────────
MIN_RESPONSE_RATE = 0.10          # Below this → heavily penalized
GOOD_RESPONSE_RATE = 0.40         # Above this → positive signal
MAX_INACTIVE_DAYS = 180           # More than 6 months → penalty
MAX_NOTICE_PREFERRED = 30         # JD prefers <30 days
MAX_NOTICE_ACCEPTABLE = 90        # Beyond this → increasing penalty
MIN_PROFILE_COMPLETENESS = 40.0   # Below this → weak signal


# ── Skill Categories for JD ──────────────────────────────────────────
JD_ABSOLUTE_SKILLS = {
    # Embeddings & Retrieval
    "Sentence Transformers", "Embeddings", "Information Retrieval",
    "FAISS", "Qdrant", "Pinecone", "Milvus", "Weaviate",
    # Python
    "Python",
    # Evaluation
    "A/B Testing",
}

JD_PREFERRED_SKILLS = {
    # LLM fine-tuning
    "Fine-tuning LLMs", "LoRA", "PEFT",
    # Learning to rank
    "XGBoost", "LightGBM",
    # ML/DL
    "PyTorch", "TensorFlow", "NLP", "Deep Learning", "Machine Learning",
    "Transformers", "MLOps", "Model Deployment",
    # GenAI
    "RAG", "LangChain",
    # Data
    "Spark", "Airflow", "Data Pipelines",
    # Infra
    "Docker", "Kubernetes", "AWS", "GCP", "Azure",
}

JD_IRRELEVANT_SKILLS = {
    "Photoshop", "Illustrator", "Figma", "SEO", "Content Writing",
    "Sales", "Marketing", "Accounting", "SAP", "Six Sigma",
    "PowerPoint", "Excel", "Salesforce CRM", "Scrum",
}

# ── Embedding Model ─────────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# ── Retrieval ────────────────────────────────────────────────────────
BM25_TOP_K = 500
VECTOR_TOP_K = 500
HYBRID_TOP_K = 500
FINAL_TOP_K = 100
