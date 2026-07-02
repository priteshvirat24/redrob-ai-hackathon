"""
Online Demo Pipeline.
Orchestrates the full Agentic AI workflow using the asyncio DAG Orchestrator.
Uses LLMs, Tavily Enrichment, and the Knowledge Graph to build deep intelligence.
"""

import sys
import os
import logging
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.orchestrator import DAGOrchestrator
from utils.observability import time_it, MetricsRegistry

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

@time_it("Demo Orchestration")
async def run_demo():
    logger.info("Initializing Online Demo Pipeline...")
    orchestrator = DAGOrchestrator(provider_name="freellm")
    
    sample_jd = "Looking for a Senior Backend Engineer with Python, FastAPI, and strong system design skills. Must have experience in high-growth startups."
    sample_candidate = {
        "candidate_id": "CAND-001",
        "profile": {"anonymized_name": "Alice Smith", "summary": "Backend developer building microservices in Python and Rust."},
        "career_history": [{"company": "TechCorp", "title": "Software Engineer", "technologies": ["Python", "FastAPI"]}]
    }
    
    # Run the DAG
    results = await orchestrator.execute_dag(sample_jd, sample_candidate)
    
    logger.info(f"Final Output: {results}")
    logger.info("Demo complete!")

if __name__ == "__main__":
    asyncio.run(run_demo())
    MetricsRegistry.print_report()

