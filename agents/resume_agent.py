"""
Resume Agent.
Extracts deep insights (leadership, projects) from sparse resume data.
"""

from pydantic import BaseModel, Field
from typing import List
from agents.base import BaseAgent

class ResumeIntelligence(BaseModel):
    inferred_leadership: bool = Field(description="Did they lead teams or projects?")
    key_projects: List[str] = Field(description="Major impactful projects")
    transferable_skills: List[str] = Field(description="Skills not explicitly listed but inferred from experience")

class ResumeAgent(BaseAgent):
    def run(self, profile_text: str, career_history: str) -> ResumeIntelligence | None:
        prompt = f"Profile:\n{profile_text}\n\nHistory:\n{career_history}"
        system = "Analyze the candidate's career history and extract inferred intelligence. Find transferable skills they likely have but didn't list."
        return self.provider.structured_completion(system, prompt, ResumeIntelligence)
