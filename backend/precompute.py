"""
Pre-computation Pipeline.
Runs offline before the ranking step to extract features, compute embeddings, and build indexes.
Saves artifacts to disk for the 5-min CPU-only ranker.
"""

import sys
import os
import json
import pickle
from pathlib import Path
import logging
from tqdm import tqdm
import numpy as np

# Add project root to path so we can run this directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.data.loader import iter_candidates, load_jd_text
from backend.agents.profiler import run_profiler
from backend.agents.honeypot import run_honeypot_detector
from backend.agents.skills import score_skills
from backend.agents.behavioral import score_behavior
from backend.core.config import PRECOMPUTED_DIR, EMBEDDING_MODEL, EMBEDDING_DIM

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Note: We import sentence_transformers here so it's not required during ranking
# if we just load the numpy arrays. But we'll likely need it for JD embedding anyway.
HAS_ST = False
try:
    from sentence_transformers import SentenceTransformer
    HAS_ST = True
except ImportError:
    logger.warning("sentence_transformers not installed. Using dummy embeddings for local dev.")


def build_features(candidates_iter):
    """Extract structured features for all candidates."""
    features_dict = {}
    
    logger.info("Extracting candidate features...")
    for candidate in tqdm(candidates_iter, desc="Profiling"):
        # Run agents
        f = run_profiler(candidate)
        f = run_honeypot_detector(candidate, f)
        f = score_skills(candidate, f)
        f = score_behavior(candidate, f)
        
        features_dict[candidate.candidate_id] = f
        
    return features_dict


def compute_embeddings(features_dict, jd_text):
    """Compute embeddings for all candidates and JD."""
    cids = list(features_dict.keys())
    texts = [features_dict[cid].career_text for cid in cids]
    
    if HAS_ST:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        model = SentenceTransformer(EMBEDDING_MODEL)
        
        # 1. JD Embedding
        logger.info("Computing JD embedding...")
        jd_embedding = model.encode(jd_text, normalize_embeddings=True)
        
        # 2. Candidate Embeddings
        logger.info("Computing candidate embeddings...")
        batch_size = 256
        embeddings = model.encode(texts, batch_size=batch_size, show_progress_bar=True, normalize_embeddings=True)
    else:
        logger.info("Using dummy embeddings...")
        np.random.seed(42)
        jd_embedding = np.random.randn(EMBEDDING_DIM)
        jd_embedding = jd_embedding / np.linalg.norm(jd_embedding)
        
        embeddings = np.random.randn(len(cids), EMBEDDING_DIM)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / norms
    
    # 3. Calculate semantic similarity directly here to save time during ranking
    logger.info("Calculating semantic similarities...")
    similarities = np.dot(embeddings, jd_embedding.T).flatten()
    
    # Update features with semantic score
    for i, cid in enumerate(cids):
        # Scale from [-1, 1] to [0, 1]
        sim = float(similarities[i])
        scaled_sim = (sim + 1) / 2.0
        features_dict[cid].semantic_score = scaled_sim
        
    return jd_embedding, embeddings, cids


def save_artifacts(features_dict, jd_embedding, embeddings, cids):
    """Save all precomputed artifacts to disk."""
    logger.info(f"Saving artifacts to {PRECOMPUTED_DIR}...")
    
    # Save features
    features_path = PRECOMPUTED_DIR / "features.pkl"
    with open(features_path, "wb") as f:
        pickle.dump(features_dict, f)
        
    # Save embeddings
    np.save(PRECOMPUTED_DIR / "jd_embedding.npy", jd_embedding)
    np.save(PRECOMPUTED_DIR / "candidate_embeddings.npy", embeddings)
    
    # Save IDs mapping for embeddings
    with open(PRECOMPUTED_DIR / "candidate_ids.json", "w") as f:
        json.dump(cids, f)
        
    logger.info("Pre-computation complete.")


def run():
    # 1. Load data
    jd_text = load_jd_text()
    
    # 2. Feature extraction
    features_dict = build_features(iter_candidates())
    
    # 3. Embeddings (requires sentence-transformers)
    jd_embedding, embeddings, cids = compute_embeddings(features_dict, jd_text)
    
    # 4. Save
    save_artifacts(features_dict, jd_embedding, embeddings, cids)


if __name__ == "__main__":
    run()
