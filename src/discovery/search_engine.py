"""Search engine for discovering businesses across multiple sources."""

import asyncio
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.logger import logger
from utils.rate_limiter import rate_limiter
from config.constants import INDUSTRY_KEYWORDS
from config.settings import settings

@dataclass
class BusinessLead:
    """Represents a discovered business lead."""
    
    name: str
    business_id: str
    source: str
    industry: str
    location: str
    
    # Basic contact info (if available from discovery)
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    
    # Metadata
    confidence_score: float = 0.0
    discovered_at: datetime = field(default_factory=datetime.now)
    raw_data: Dict[str, Any] = field(default_factory=dict)

class SearchEngine:
    """Multi-source business search engine."""
    
    def __init__(self):
        self.sources = [
            "google_places",
            "yelp", 
            "yellow_pages",
            "linkedin",
            "industry_specific"
        ]
    
    async def search_businesses(
        self, 
        industry: str, 
        location: str, 
        limit: int = 10
    ) -> List[BusinessLead]:
        """Search for businesses across multiple sources.
        
        Args:
            industry: Business industry/category
            location: Geographic location
            limit: Maximum number of results
            
        Returns:
            List of discovered business leads
        """
        logger.info(f"Starting business search: {industry} in {location} (limit: {limit})")
        
        # Get relevant keywords for the industry
        keywords = self._get_industry_keywords(industry)
        
        # Search across all sources concurrently
        search_tasks = [
            self._search_google_places(industry, location, keywords, limit // 2),
            self._search_yelp(industry, location, keywords, limit // 3),
            self._search_directories(industry, location, keywords, limit // 4),
            self._search_linkedin_companies(industry, location, keywords, limit // 5)
        ]
        
        results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Combine results and remove duplicates
        all_leads = []
        for result in results:
            if isinstance(result, list):
                all_leads.extend(result)
            else:
                logger.warning(f"Search error: {result}")
        
        # Deduplicate and limit results
        unique_leads = self._deduplicate_leads(all_leads)
        final_leads = unique_leads[:limit]
        
        logger.info(f"Found {len(final_leads)} unique businesses")
        return final_leads
    
    def _get_industry_keywords(self, industry: str) -> List[str]:
        """Get relevant keywords for an industry."""
        return INDUSTRY_KEYWORDS.get(industry.lower(), [industry])
    
    async def _search_google_places(
        self, 
        industry: str, 
        location: str, 
        keywords: List[str], 
        limit: int
    ) -> List[BusinessLead]:
        """Simulate Google Places API search."""
        await rate_limiter.wait_for_tokens("google_places", 1)
        
        # TODO: Replace with real Google Places API integration
        if not settings.ENABLE_SIMULATION:
            return []
        
        logger.debug("Searching Google Places (simulated)")
        await asyncio.sleep(0.1)  # Simulate API delay
        
        leads = []
        for i in range(min(limit, 5)):
            business_id = f"google_places_{random.randint(1000, 9999)}"
            lead = BusinessLead(
                name=f"Google Places {industry.title()} {i+1}",
                business_id=business_id,
                source="google_places",
                industry=industry,
                location=location,
                address=f"{random.randint(100, 999)} Main St, {location}",
                phone=f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                website=f"https://example-{business_id}.com",
                confidence_score=random.uniform(0.7, 0.95),
                raw_data={
                    "place_id": business_id,
                    "rating": random.uniform(3.5, 5.0),
                    "review_count": random.randint(10, 500),
                    "price_level": random.randint(1, 4)
                }
            )
            leads.append(lead)
        
        return leads
    
    async def _search_yelp(
        self, 
        industry: str, 
        location: str, 
        keywords: List[str], 
        limit: int
    ) -> List[BusinessLead]:
        """Simulate Yelp Fusion API search."""
        await rate_limiter.wait_for_tokens("yelp", 1)
        
        # TODO: Replace with real Yelp Fusion API integration
        if not settings.ENABLE_SIMULATION:
            return []
        
        logger.debug("Searching Yelp (simulated)")
        await asyncio.sleep(0.2)  # Simulate API delay
        
        leads = []
        for i in range(min(limit, 3)):
            business_id = f"yelp_{random.randint(1000, 9999)}"
            lead = BusinessLead(
                name=f"Yelp {industry.title()} {i+1}",
                business_id=business_id,
                source="yelp",
                industry=industry,
                location=location,
                address=f"{random.randint(100, 999)} Commercial Ave, {location}",
                phone=f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                website=f"https://example-{business_id}.com",
                confidence_score=random.uniform(0.6, 0.9),
                raw_data={
                    "yelp_id": business_id,
                    "rating": random.uniform(3.0, 5.0),
                    "review_count": random.randint(5, 300),
                    "categories": [industry, "business"],
                    "price": "$" * random.randint(1, 4)
                }
            )
            leads.append(lead)
        
        return leads
    
    async def _search_directories(
        self, 
        industry: str, 
        location: str, 
        keywords: List[str], 
        limit: int
    ) -> List[BusinessLead]:
        """Simulate business directory searches (Yellow Pages, etc.)."""
        await rate_limiter.wait_for_tokens("yellow_pages", 1)
        
        # TODO: Replace with real directory API integrations
        if not settings.ENABLE_SIMULATION:
            return []
        
        logger.debug("Searching business directories (simulated)")
        await asyncio.sleep(0.15)  # Simulate scraping delay
        
        leads = []
        for i in range(min(limit, 2)):
            business_id = f"directory_{random.randint(1000, 9999)}"
            lead = BusinessLead(
                name=f"Directory {industry.title()} {i+1}",
                business_id=business_id,
                source="yellow_pages",
                industry=industry,
                location=location,
                address=f"{random.randint(100, 999)} Business Blvd, {location}",
                phone=f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                confidence_score=random.uniform(0.5, 0.8),
                raw_data={
                    "directory_id": business_id,
                    "listing_type": "premium" if random.random() > 0.5 else "basic",
                    "years_in_business": random.randint(1, 25)
                }
            )
            leads.append(lead)
        
        return leads
    
    async def _search_linkedin_companies(
        self, 
        industry: str, 
        location: str, 
        keywords: List[str], 
        limit: int
    ) -> List[BusinessLead]:
        """Simulate LinkedIn company search."""
        await rate_limiter.wait_for_tokens("linkedin", 1)
        
        # TODO: Replace with real LinkedIn API integration
        if not settings.ENABLE_SIMULATION:
            return []
        
        logger.debug("Searching LinkedIn companies (simulated)")
        await asyncio.sleep(0.3)  # Simulate API delay
        
        leads = []
        for i in range(min(limit, 2)):
            business_id = f"linkedin_{random.randint(1000, 9999)}"
            lead = BusinessLead(
                name=f"LinkedIn {industry.title()} {i+1}",
                business_id=business_id,
                source="linkedin",
                industry=industry,
                location=location,
                website=f"https://example-{business_id}.com",
                confidence_score=random.uniform(0.6, 0.85),
                raw_data={
                    "linkedin_id": business_id,
                    "company_size": f"{random.randint(10, 500)}+ employees",
                    "founded_year": random.randint(1990, 2020),
                    "specialties": keywords[:3]
                }
            )
            leads.append(lead)
        
        return leads
    
    def _deduplicate_leads(self, leads: List[BusinessLead]) -> List[BusinessLead]:
        """Remove duplicate leads based on name and location similarity."""
        unique_leads = []
        seen_names = set()
        
        for lead in leads:
            # Simple deduplication by normalized name
            normalized_name = lead.name.lower().strip()
            if normalized_name not in seen_names:
                seen_names.add(normalized_name)
                unique_leads.append(lead)
        
        return unique_leads

# TODO: Future enhancements for discovery:
# - Real API integrations (Google Places, Yelp Fusion, etc.)
# - Advanced deduplication using fuzzy matching
# - Business validation and verification
# - Industry-specific search sources
# - Geographic radius and precision controls
# - Search result ranking and scoring algorithms
# - Caching of search results to avoid duplicate API calls