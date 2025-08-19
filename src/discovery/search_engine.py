"""Business search engine abstraction and implementations."""

import asyncio
import random
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Add root directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.logger import logger
from src.utils.rate_limiter import rate_limiters


@dataclass
class BusinessSearchResult:
    """Represents a business found by search engines."""
    
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    source: str = "unknown"
    confidence_score: float = 0.5
    raw_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "website": self.website,
            "industry": self.industry,
            "source": self.source,
            "confidence_score": self.confidence_score,
            "raw_data": self.raw_data
        }


class SearchEngine(ABC):
    """Abstract base class for business search engines."""
    
    @abstractmethod
    async def search_businesses(
        self, 
        industry: str, 
        location: str, 
        limit: int = 10
    ) -> List[BusinessSearchResult]:
        """Search for businesses matching criteria."""
        pass
    
    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return the name of this search source."""
        pass


class MockGoogleMapsSearch(SearchEngine):
    """Mock Google Maps search implementation."""
    
    @property
    def source_name(self) -> str:
        return "google_maps"
    
    async def search_businesses(
        self, 
        industry: str, 
        location: str, 
        limit: int = 10
    ) -> List[BusinessSearchResult]:
        """Mock search implementation."""
        logger.info(f"Mock Google Maps search: {industry} in {location} (limit: {limit})")
        
        # Simulate rate limiting
        rate_limiters["google"].wait_if_needed()
        
        # Simulate API delay
        await asyncio.sleep(0.5)
        
        results = []
        for i in range(min(limit, 5)):  # Max 5 mock results
            business = BusinessSearchResult(
                name=f"Sample {industry.title()} Business {i+1}",
                address=f"{100 + i*10} Main St, {location}",
                phone=f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}",
                website=f"https://business{i+1}.example.com",
                industry=industry,
                source=self.source_name,
                confidence_score=random.uniform(0.6, 0.9),
                raw_data={
                    "place_id": f"mock_place_{i+1}",
                    "rating": round(random.uniform(3.5, 5.0), 1),
                    "review_count": random.randint(10, 500)
                }
            )
            results.append(business)
        
        logger.info(f"Found {len(results)} mock businesses from Google Maps")
        return results


class MockYelpSearch(SearchEngine):
    """Mock Yelp search implementation."""
    
    @property
    def source_name(self) -> str:
        return "yelp"
    
    async def search_businesses(
        self, 
        industry: str, 
        location: str, 
        limit: int = 10
    ) -> List[BusinessSearchResult]:
        """Mock search implementation."""
        logger.info(f"Mock Yelp search: {industry} in {location} (limit: {limit})")
        
        # Simulate rate limiting
        rate_limiters["yelp"].wait_if_needed()
        
        # Simulate API delay
        await asyncio.sleep(0.3)
        
        results = []
        for i in range(min(limit, 3)):  # Max 3 mock results
            business = BusinessSearchResult(
                name=f"Yelp {industry.title()} Spot {i+1}",
                address=f"{200 + i*15} Second Ave, {location}",
                phone=f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}",
                website=f"https://yelpbiz{i+1}.example.com",
                industry=industry,
                source=self.source_name,
                confidence_score=random.uniform(0.5, 0.8),
                raw_data={
                    "yelp_id": f"mock_yelp_{i+1}",
                    "rating": round(random.uniform(3.0, 5.0), 1),
                    "price": "$" * random.randint(1, 4),
                    "categories": [industry, "local_business"]
                }
            )
            results.append(business)
        
        logger.info(f"Found {len(results)} mock businesses from Yelp")
        return results


class MockYellowPagesSearch(SearchEngine):
    """Mock Yellow Pages search implementation."""
    
    @property
    def source_name(self) -> str:
        return "yellow_pages"
    
    async def search_businesses(
        self, 
        industry: str, 
        location: str, 
        limit: int = 10
    ) -> List[BusinessSearchResult]:
        """Mock search implementation."""
        logger.info(f"Mock Yellow Pages search: {industry} in {location} (limit: {limit})")
        
        # Simulate rate limiting
        rate_limiters["default"].wait_if_needed()
        
        # Simulate API delay
        await asyncio.sleep(0.4)
        
        results = []
        for i in range(min(limit, 2)):  # Max 2 mock results
            business = BusinessSearchResult(
                name=f"YP {industry.title()} Co. {i+1}",
                address=f"{300 + i*20} Third St, {location}",
                phone=f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}",
                website=f"https://ypbiz{i+1}.example.com",
                industry=industry,
                source=self.source_name,
                confidence_score=random.uniform(0.4, 0.7),
                raw_data={
                    "yp_id": f"mock_yp_{i+1}",
                    "years_in_business": random.randint(1, 25),
                    "verified": random.choice([True, False])
                }
            )
            results.append(business)
        
        logger.info(f"Found {len(results)} mock businesses from Yellow Pages")
        return results


class BusinessSearchEngine:
    """Main business search orchestrator."""
    
    def __init__(self):
        self.search_engines = [
            MockGoogleMapsSearch(),
            MockYelpSearch(),
            MockYellowPagesSearch()
        ]
    
    async def search_all_sources(
        self, 
        industry: str, 
        location: str, 
        limit: int = 10
    ) -> List[BusinessSearchResult]:
        """Search across all available sources."""
        logger.info(f"Starting multi-source search: {industry} in {location}")
        
        all_results = []
        
        # Run searches in parallel
        search_tasks = []
        for engine in self.search_engines:
            task = engine.search_businesses(industry, location, limit)
            search_tasks.append(task)
        
        # Wait for all searches to complete
        results_lists = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Collect successful results
        for i, results in enumerate(results_lists):
            if isinstance(results, Exception):
                engine_name = self.search_engines[i].source_name
                logger.error(f"Error in {engine_name} search: {results}")
            else:
                all_results.extend(results)
        
        # Remove duplicates (simple name-based deduplication)
        unique_results = self._deduplicate_results(all_results)
        
        logger.info(f"Total unique businesses found: {len(unique_results)}")
        return unique_results[:limit]  # Limit final results
    
    def _deduplicate_results(self, results: List[BusinessSearchResult]) -> List[BusinessSearchResult]:
        """Remove duplicate businesses based on name similarity."""
        seen_names = set()
        unique_results = []
        
        for business in results:
            # Simple deduplication by normalized name
            normalized_name = business.name.lower().strip()
            if normalized_name not in seen_names:
                seen_names.add(normalized_name)
                unique_results.append(business)
        
        return unique_results