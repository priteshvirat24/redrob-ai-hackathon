"""
Knowledge Graph for Candidate Intelligence.
Builds an in-memory graph mapping Skills, Domains, Companies, Roles, Projects, and Technologies.
Used by both the Demo orchestration and Offline Ranking (via caching).
"""

import networkx as nx
import logging
from typing import List, Dict, Set

logger = logging.getLogger(__name__)

class CandidateKnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_company(self, name: str, industry: str = None):
        if not name: return
        self.graph.add_node(name, type="Company")
        if industry:
            self.graph.add_node(industry, type="Industry")
            self.graph.add_edge(name, industry, relation="BELONGS_TO")

    def add_skill(self, name: str, domain: str = "General"):
        if not name: return
        self.graph.add_node(name, type="Skill")
        self.graph.add_node(domain, type="Domain")
        self.graph.add_edge(name, domain, relation="PART_OF")
        
    def add_technology(self, name: str):
        if not name: return
        self.graph.add_node(name, type="Technology")
        
    def link_skill_to_technology(self, skill: str, tech: str):
        self.graph.add_edge(tech, skill, relation="IMPLEMENTS")

    def link_candidate_to_skill(self, cid: str, skill: str):
        self.graph.add_node(cid, type="Candidate")
        if skill in self.graph:
            self.graph.add_edge(cid, skill, relation="HAS_SKILL")

    def link_candidate_to_company(self, cid: str, company: str, title: str):
        self.graph.add_node(cid, type="Candidate")
        if company in self.graph:
            self.graph.add_edge(cid, company, relation="WORKED_AT", title=title)
            
    def link_candidate_to_project(self, cid: str, project_name: str, technologies: List[str]):
        self.graph.add_node(cid, type="Candidate")
        self.graph.add_node(project_name, type="Project")
        self.graph.add_edge(cid, project_name, relation="BUILT")
        for tech in technologies:
            self.add_technology(tech)
            self.graph.add_edge(project_name, tech, relation="BUILT_WITH")
            self.graph.add_edge(cid, tech, relation="USES")

    def compute_candidate_centrality(self) -> Dict[str, float]:
        try:
            return nx.pagerank(self.graph)
        except Exception as e:
            logger.error(f"Failed to compute centrality: {e}")
            return {}

    def get_related_skills(self, skill: str, max_depth: int = 2) -> Set[str]:
        if skill not in self.graph:
            return set()
        
        related = set()
        successors = list(self.graph.successors(skill))
        for domain in successors:
            if self.graph.nodes[domain].get("type") == "Domain":
                predecessors = list(self.graph.predecessors(domain))
                for s in predecessors:
                    if self.graph.nodes[s].get("type") == "Skill":
                        related.add(s)
        return related

# Singleton instance for the runtime
kg = CandidateKnowledgeGraph()

