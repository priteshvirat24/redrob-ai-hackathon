"""
Core configuration for the AI Recruiting Copilot.
Centralizes all paths, weights, thresholds, and model settings.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict
from datetime import date


# -- Paths --
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = PROJECT_ROOT / "datasets" / "full"
# Fallback to the original bracketed name if datasets/full does not exist
if not DATASET_DIR.exists():
    _alt = PROJECT_ROOT / "[PUB] India_runs_data_and_ai_challenge" / "India_runs_data_and_ai_challenge"
    if _alt.exists():
        DATASET_DIR = _alt
CANDIDATES_FILE = DATASET_DIR / "candidates.jsonl"
JD_FILE = DATASET_DIR / "job_description.txt"
PRECOMPUTED_DIR = PROJECT_ROOT / "intelligence" / "feature_store" / "precomputed"

# Ensure precomputed dir exists
PRECOMPUTED_DIR.mkdir(parents=True, exist_ok=True)

# -- Shared Reference Date (used by all agents) --
REF_DATE = date(2026, 5, 30)


# -- Scoring Weights (rebalanced for real retrieval signal) --
@dataclass
class ScoringWeights:
    """Configurable weights for the composite ranking score."""
    semantic_match: float = 0.34     # retrieval (dense + BM25 + rerank)
    title_relevance: float = 0.20
    skill_match: float = 0.18
    experience_fit: float = 0.10
    career_coherence: float = 0.08
    education: float = 0.04
    behavioral: float = 0.06

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


# -- Title Categories --
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


# -- JD Disqualifiers --
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


# -- Experience Band --
IDEAL_YOE_MIN = 5.0
IDEAL_YOE_MAX = 9.0
ACCEPTABLE_YOE_MIN = 3.0
ACCEPTABLE_YOE_MAX = 14.0


# -- Location --
PREFERRED_LOCATIONS = {
    "Pune", "Noida", "Hyderabad", "Mumbai", "Delhi", "Delhi NCR",
    "Gurgaon", "Gurugram", "Bangalore", "Bengaluru", "Chennai",
    "Pune, Maharashtra", "Noida, Uttar Pradesh",
}

PREFERRED_COUNTRY = "India"


# -- Behavioral Thresholds --
MIN_RESPONSE_RATE = 0.10          # Below this: heavily penalized
GOOD_RESPONSE_RATE = 0.40         # Above this: positive signal
MAX_INACTIVE_DAYS = 180           # More than 6 months: penalty
MAX_NOTICE_PREFERRED = 30         # JD prefers <30 days
MAX_NOTICE_ACCEPTABLE = 90        # Beyond this: increasing penalty
MIN_PROFILE_COMPLETENESS = 40.0   # Below this: weak signal


# -- Skill Categories for JD --
JD_ABSOLUTE_SKILLS = {
    # Embeddings and Retrieval
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

# Normalized lookup sets for fuzzy skill matching
def _normalize_skill(name: str) -> str:
    """Normalize a skill name for matching."""
    return " ".join(name.lower().strip().replace("-", " ").replace("_", " ").split())

# Alias map for common variants
SKILL_ALIASES = {
    "sentencetransformers": "sentence transformers",
    "sentence transformer": "sentence transformers",
    "pytorch": "pytorch",
    "tensor flow": "tensorflow",
    "scikit learn": "scikit-learn",
    "lang chain": "langchain",
    "xg boost": "xgboost",
    "light gbm": "lightgbm",
}

JD_ABSOLUTE_SKILLS_NORM = {_normalize_skill(s) for s in JD_ABSOLUTE_SKILLS}
JD_PREFERRED_SKILLS_NORM = {_normalize_skill(s) for s in JD_PREFERRED_SKILLS}
JD_IRRELEVANT_SKILLS_NORM = {_normalize_skill(s) for s in JD_IRRELEVANT_SKILLS}


# -- Embedding Model --
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# -- Cross-Encoder Model --
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# -- Retrieval --
BM25_TOP_K = 500
VECTOR_TOP_K = 500
HYBRID_TOP_K = 500
CROSS_ENCODER_TOP_K = 200
FINAL_TOP_K = 100

# -- JD Query (focused requirements, not the whole doc) --
JD_QUERY = (
    "Senior AI Engineer with strong Python skills, "
    "experience building embedding-based retrieval systems, "
    "vector databases (FAISS, Qdrant, Pinecone), "
    "sentence transformers, semantic search, NLP, "
    "PyTorch or TensorFlow, RAG pipelines, "
    "LLM fine-tuning, learning-to-rank, "
    "MLOps, model deployment, evaluation frameworks, A/B testing. "
    "Product company experience preferred over consulting. "
    "5-9 years experience. India-based, Pune or Noida preferred."
)
