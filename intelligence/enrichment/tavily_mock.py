"""
Tavily Web Search Enrichment (Mocked).
Searches the web for missing candidate information like GitHub, Portfolios, or Publications.
"""

import logging

logger = logging.getLogger(__name__)

class TavilyEnricher:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        
    def enrich_candidate(self, name: str, company: str) -> dict:
        """
        Mock implementation of Tavily search.
        In a real scenario, this would use the Tavily API to find GitHub profiles,
        personal websites, or Google Scholar links.
        """
        logger.info(f"Tavily Search: Searching for {name} at {company}...")
        
        # Return mock data based on simple heuristics to demonstrate the pipeline
        has_github = len(name) % 2 == 0
        
        enrichment = {
            "found_github": has_github,
            "github_url": f"https://github.com/{name.lower().replace(' ', '')}" if has_github else None,
            "inferred_open_source_activity": "High" if has_github else "Unknown",
            "publications": []
        }
        
        return enrichment
