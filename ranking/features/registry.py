"""
Feature Registry.
Allows pluggable feature scoring modules that can be dynamically toggled for ablation studies.
"""

from typing import Dict, Callable, Any
from config.types import Candidate, CandidateFeatures
import logging

logger = logging.getLogger(__name__)

class FeatureRegistry:
    _features: Dict[str, Callable[[Candidate, CandidateFeatures], None]] = {}
    _active_features: Dict[str, bool] = {}

    @classmethod
    def register(cls, name: str, default_active: bool = True):
        def decorator(func: Callable[[Candidate, CandidateFeatures], None]):
            cls._features[name] = func
            cls._active_features[name] = default_active
            return func
        return decorator

    @classmethod
    def toggle(cls, name: str, active: bool):
        if name in cls._active_features:
            cls._active_features[name] = active
            logger.info(f"Feature '{name}' set to {'ON' if active else 'OFF'}")
        else:
            logger.warning(f"Feature '{name}' not found in registry.")

    @classmethod
    def apply_all(cls, candidate: Candidate, features: CandidateFeatures):
        for name, func in cls._features.items():
            if cls._active_features[name]:
                try:
                    func(candidate, features)
                except Exception as e:
                    logger.error(f"Error applying feature '{name}': {e}")
