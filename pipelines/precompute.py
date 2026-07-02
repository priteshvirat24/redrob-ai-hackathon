"""
Pre-computation Pipeline.
Runs offline to extract features, compute real embeddings, build BM25 index,
perform hybrid retrieval with RRF, and cross-encoder rerank of top candidates.
Saves all artifacts to disk for the 5-min CPU-only ranker.
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

from intelligence.feature_store.loader import iter_candidates, load_jd_text
from ranking.profiler import run_profiler
from ranking.honeypot import run_honeypot_detector
from ranking.skills import score_skills
from ranking.behavioral import score_behavior
from config.settings import (
    PRECOMPUTED_DIR, EMBEDDING_MODEL, EMBEDDING_DIM,
    CROSS_ENCODER_MODEL, CROSS_ENCODER_TOP_K, JD_QUERY,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Import sentence_transformers -- fail loudly if missing, no random fallback
try:
    from sentence_transformers import SentenceTransformer, CrossEncoder
except ImportError:
    raise RuntimeError(
        "sentence-transformers is required but not installed. "
        "Run: pip install sentence-transformers torch"
    )

from rank_bm25 import BM25Okapi


def build_features(candidates_iter):
    """Extract structured features for all candidates."""
    features_dict = {}

    logger.info("Extracting candidate features...")
    for candidate in tqdm(candidates_iter, desc="Profiling"):
        f = run_profiler(candidate)
        f = run_honeypot_detector(candidate, f)
        f = score_skills(candidate, f)
        f = score_behavior(candidate, f)

        features_dict[candidate.candidate_id] = f

    return features_dict


def build_candidate_documents(features_dict):
    """Build combined candidate documents for embedding (headline + summary + career)."""
    cids = list(features_dict.keys())
    docs = []
    for cid in cids:
        f = features_dict[cid]
        # Combine profile_text AND career_text (the audit found we only used career_text)
        doc = f"{f.profile_text} {f.career_text}".strip()
        if not doc:
            doc = "No profile information available."
        docs.append(doc)
    return cids, docs


def compute_embeddings_and_bm25(cids, docs, jd_query):
    """Compute dense embeddings + BM25 index. Return both."""
    logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)

    # 1. JD query embedding (focused requirements, not the whole doc)
    logger.info("Computing JD query embedding...")
    jd_embedding = model.encode(jd_query, normalize_embeddings=True)

    # 2. Candidate embeddings (batched)
    logger.info(f"Computing embeddings for {len(docs)} candidates...")
    batch_size = 256
    embeddings = model.encode(
        docs, batch_size=batch_size, show_progress_bar=True, normalize_embeddings=True
    )

    # 3. Dense cosine similarities
    logger.info("Computing dense similarities...")
    dense_sims = np.dot(embeddings, jd_embedding.T).flatten()

    # 4. BM25 index
    logger.info("Building BM25 index...")
    tokenized_docs = [doc.lower().split() for doc in docs]
    bm25 = BM25Okapi(tokenized_docs)
    tokenized_query = jd_query.lower().split()
    bm25_scores = bm25.get_scores(tokenized_query)

    return jd_embedding, embeddings, dense_sims, bm25, bm25_scores


def reciprocal_rank_fusion(dense_sims, bm25_scores, cids, k=60):
    """
    Combine dense and BM25 scores using Reciprocal Rank Fusion.
    Returns fused scores in [0,1] (normalized).
    """
    n = len(cids)

    # Rank by dense similarity (descending)
    dense_order = np.argsort(-dense_sims)
    dense_ranks = np.empty(n, dtype=int)
    dense_ranks[dense_order] = np.arange(n)

    # Rank by BM25 (descending)
    bm25_order = np.argsort(-bm25_scores)
    bm25_ranks = np.empty(n, dtype=int)
    bm25_ranks[bm25_order] = np.arange(n)

    # RRF scores
    rrf = 1.0 / (k + dense_ranks + 1) + 1.0 / (k + bm25_ranks + 1)

    # Normalize to [0, 1]
    rrf_min, rrf_max = rrf.min(), rrf.max()
    if rrf_max > rrf_min:
        rrf_norm = (rrf - rrf_min) / (rrf_max - rrf_min)
    else:
        rrf_norm = np.zeros(n)

    return rrf_norm


def cross_encoder_rerank(cids, docs, rrf_scores, jd_query, top_k=200):
    """
    Rerank the top candidates using a cross-encoder for better precision.
    Blends cross-encoder score with RRF score.
    """
    logger.info(f"Cross-encoder reranking top {top_k} candidates...")
    ce_model = CrossEncoder(CROSS_ENCODER_MODEL)

    # Select top-k by RRF
    top_indices = np.argsort(-rrf_scores)[:top_k]

    # Build pairs for cross-encoder
    pairs = [(jd_query, docs[i]) for i in top_indices]

    # Score with cross-encoder
    ce_scores_raw = ce_model.predict(pairs, show_progress_bar=True, batch_size=64)

    # Normalize cross-encoder scores to [0,1]
    ce_min, ce_max = ce_scores_raw.min(), ce_scores_raw.max()
    if ce_max > ce_min:
        ce_norm = (ce_scores_raw - ce_min) / (ce_max - ce_min)
    else:
        ce_norm = np.zeros(len(ce_scores_raw))

    # Blend: 0.6 * cross_encoder + 0.4 * fused_rrf (for the reranked set)
    final_scores = rrf_scores.copy()
    for idx_in_top, global_idx in enumerate(top_indices):
        blended = 0.6 * ce_norm[idx_in_top] + 0.4 * rrf_scores[global_idx]
        final_scores[global_idx] = blended

    return final_scores


def save_artifacts(features_dict, jd_embedding, embeddings, cids):
    """Save all precomputed artifacts to disk."""
    logger.info(f"Saving artifacts to {PRECOMPUTED_DIR}...")

    with open(PRECOMPUTED_DIR / "features.pkl", "wb") as f:
        pickle.dump(features_dict, f)

    np.save(PRECOMPUTED_DIR / "jd_embedding.npy", jd_embedding)
    np.save(PRECOMPUTED_DIR / "candidate_embeddings.npy", embeddings)

    with open(PRECOMPUTED_DIR / "candidate_ids.json", "w") as f:
        json.dump(cids, f)

    logger.info("Pre-computation complete.")


def run(candidates_path=None):
    """Run the full pre-computation pipeline."""
    import time
    start = time.time()

    # 1. Load JD
    jd_text = load_jd_text()

    # 2. Feature extraction
    from intelligence.feature_store.loader import iter_candidates as _iter
    if candidates_path:
        features_dict = build_features(_iter(candidates_path))
    else:
        features_dict = build_features(_iter())

    # 3. Build candidate documents
    cids, docs = build_candidate_documents(features_dict)

    # 4. Dense embeddings + BM25
    jd_embedding, embeddings, dense_sims, bm25, bm25_scores = (
        compute_embeddings_and_bm25(cids, docs, JD_QUERY)
    )

    # 5. Reciprocal Rank Fusion
    rrf_scores = reciprocal_rank_fusion(dense_sims, bm25_scores, cids)

    # 6. Cross-encoder rerank of top candidates
    final_retrieval_scores = cross_encoder_rerank(
        cids, docs, rrf_scores, JD_QUERY, top_k=CROSS_ENCODER_TOP_K
    )

    # 7. Update features with retrieval score (replaces the old semantic_score)
    for i, cid in enumerate(cids):
        features_dict[cid].semantic_score = float(final_retrieval_scores[i])

    # 8. Save
    save_artifacts(features_dict, jd_embedding, embeddings, cids)

    elapsed = time.time() - start
    logger.info(f"Total pre-computation time: {elapsed:.1f}s")


if __name__ == "__main__":
    run()
