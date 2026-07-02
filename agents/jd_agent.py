"""
JD Agent.
Uses the LLM to parse the Job Description and extract structured requirements, seniority, and hidden expectations.
"""

from pydantic import BaseModel, Field
from typing import List
from agents.base import BaseAgent

class JDOntology(BaseModel):
    core_skills: List[str] = Field(description="Must-have technical skills")
    nice_to_have: List[str] = Field(description="Preferred but not strictly required skills")
    seniority: str = Field(description="Expected seniority level (e.g. Junior, Mid, Senior, Staff)")
    hidden_expectations: List[str] = Field(description="Implicit requirements not explicitly stated (e.g. fast-paced startup experience)")
    domains: List[str] = Field(description="Core industry domains (e.g. FinTech, Healthcare AI)")

class JDAgent(BaseAgent):
    def run(self, raw_text: str) -> JDOntology | None:
        prompt = f"Analyze the following Job Description and extract the requested fields:\n\n{raw_text}"
        system = "You are an elite AI Recruiter parsing a job description to build a structured hiring ontology."
        return self.provider.structured_completion(system, prompt, JDOntology)
