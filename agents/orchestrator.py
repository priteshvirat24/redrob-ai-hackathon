"""
DAG Orchestrator for the Agentic Workflow.
Executes agents concurrently where possible (e.g. JD processing vs Candidate Profile parsing).
"""

import asyncio
import logging
from typing import Dict, Any

from agents.jd_agent import JDAgent
from agents.resume_agent import ResumeAgent
from intelligence.llm.providers import ProviderRegistry
from intelligence.knowledge_graph.kg import kg

logger = logging.getLogger(__name__)

class DAGOrchestrator:
    def __init__(self, provider_name: str = "freellm"):
        # We don't instantiate agents here directly if they are stateless,
        # but since they use the provider, we initialize them.
        self.provider_name = provider_name
        self.jd_agent = JDAgent(provider_name)
        self.resume_agent = ResumeAgent(provider_name)

    async def process_jd_async(self, jd_text: str) -> Dict[str, Any]:
        logger.info("Executing JD Agent node...")
        # Since the provider is synchronous in this implementation, we run it in a thread pool
        # to achieve pseudo-concurrency without rewriting the OpenAI client to use AsyncOpenAI.
        ontology = await asyncio.to_thread(self.jd_agent.run, jd_text)
        return {"ontology": ontology}

    async def process_candidate_async(self, candidate_data: dict) -> Dict[str, Any]:
        logger.info("Executing Resume Agent node...")
        profile_text = candidate_data.get("profile", {}).get("summary", "")
        career_history = candidate_data.get("career_history", [])
        
        intel = await asyncio.to_thread(self.resume_agent.run, profile_text, str(career_history))
        return {"candidate_intelligence": intel}

    async def execute_dag(self, jd_text: str, candidate_data: dict):
        """
        Runs the independent branches in parallel:
        Branch 1: JD parsing -> Ontology -> Knowledge Graph
        Branch 2: Resume parsing -> Intelligence -> Feature Store
        """
        logger.info("Starting DAG Execution...")
        
        # Run parallel tasks
        jd_task = asyncio.create_task(self.process_jd_async(jd_text))
        candidate_task = asyncio.create_task(self.process_candidate_async(candidate_data))
        
        results = await asyncio.gather(jd_task, candidate_task)
        
        jd_result = results[0].get("ontology")
        cand_result = results[1].get("candidate_intelligence")
        
        # Fusion node
        logger.info("DAG Fusion Node: Updating Knowledge Graph")
        if jd_result:
            for skill in getattr(jd_result, "core_skills", []):
                kg.add_skill(skill)
                
        if cand_result:
            cid = candidate_data.get("candidate_id")
            for skill in getattr(cand_result, "transferable_skills", []):
                kg.link_candidate_to_skill(cid, skill)
                
        logger.info("DAG Execution Complete.")
        return {
            "ontology": jd_result,
            "intelligence": cand_result
        }
