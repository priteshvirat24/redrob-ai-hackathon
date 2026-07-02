"""
Data loading utilities for the Redrob hackathon dataset.
Handles JSONL parsing, chunked loading, and JD text extraction.
"""

import json
import logging
from pathlib import Path
from typing import Generator, List, Optional

from config.types import Candidate
from config.settings import CANDIDATES_FILE, JD_FILE, DATASET_DIR

logger = logging.getLogger(__name__)


def load_jd_text() -> str:
    """Load the job description as plain text."""
    jd_path = JD_FILE
    if not jd_path.exists():
        # Try the docx-converted txt
        jd_path = DATASET_DIR / "job_description.txt"
    if not jd_path.exists():
        raise FileNotFoundError(f"Job description not found at {jd_path}")
    return jd_path.read_text(encoding="utf-8")


def iter_candidates(path: Optional[Path] = None) -> Generator[Candidate, None, None]:
    """
    Iterate over candidates from a JSONL file, yielding parsed Candidate objects.
    Memory-efficient: processes one candidate at a time.
    """
    filepath = path or CANDIDATES_FILE
    logger.info(f"Loading candidates from {filepath}")
    count = 0
    errors = 0

    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                yield Candidate.from_dict(data)
                count += 1
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                errors += 1
                if errors <= 5:
                    logger.warning(f"Line {line_num}: Failed to parse candidate: {e}")

    logger.info(f"Loaded {count} candidates ({errors} parse errors)")


def load_all_candidates(path: Optional[Path] = None, limit: Optional[int] = None) -> List[Candidate]:
    """Load all candidates into memory. Use limit for testing."""
    candidates = []
    for c in iter_candidates(path):
        candidates.append(c)
        if limit and len(candidates) >= limit:
            break
    logger.info(f"Loaded {len(candidates)} candidates into memory")
    return candidates


def load_raw_candidates(path: Optional[Path] = None, limit: Optional[int] = None) -> List[dict]:
    """Load raw JSON dicts without parsing into Candidate objects. Faster for feature extraction."""
    filepath = path or CANDIDATES_FILE
    candidates = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            candidates.append(json.loads(line))
            if limit and len(candidates) >= limit:
                break
    return candidates
