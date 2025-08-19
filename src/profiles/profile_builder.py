"""Business profile builder and enrichment orchestrator."""

import asyncio
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from discovery.search_engine import BusinessLead
from utils.logger import logger
from utils.rate_limiter import rate_limiter
from config.settings import settings

@dataclass
class SocialMediaProfile:
    """Social media profile information."""
    platform: str
    url: str
    followers: Optional[int] = None
    verified: bool = False
    last_post: Optional[datetime] = None
    engagement_rate: Optional[float] = None

@dataclass
class NewsArticle:
    """News article about the business."""
    title: str
    url: str
    published_date: datetime
    source: str
    sentiment: Optional[str] = None  # positive, negative, neutral

@dataclass
class BusinessProfile:
    """Complete enriched business profile."""
    
    # Core business information
    lead: BusinessLead
    
    # Enriched data
    description: Optional[str] = None
    founded_year: Optional[int] = None
    employee_count: Optional[str] = None
    annual_revenue: Optional[str] = None
    
    # Social media presence
    social_profiles: List[SocialMediaProfile] = field(default_factory=list)
    
    # News and media
    news_articles: List[NewsArticle] = field(default_factory=list)
    
    # Directory listings
    directory_listings: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Enrichment metadata
    enrichment_score: float = 0.0
    enriched_at: datetime = field(default_factory=datetime.now)
    enrichment_sources: List[str] = field(default_factory=list)

class ProfileBuilder:
    """Builds enriched business profiles from leads."""
    
    async def build_profiles(self, leads: List[BusinessLead]) -> List[BusinessProfile]:
        """Build enriched profiles for a list of business leads.
        
        Args:
            leads: List of business leads to enrich
            
        Returns:
            List of enriched business profiles
        """
        logger.info(f"Building profiles for {len(leads)} business leads")
        
        # Process leads concurrently
        tasks = [self._build_single_profile(lead) for lead in leads]
        profiles = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out any errors
        valid_profiles = []
        for profile in profiles:
            if isinstance(profile, BusinessProfile):
                valid_profiles.append(profile)
            else:
                logger.warning(f"Profile building error: {profile}")
        
        logger.info(f"Successfully built {len(valid_profiles)} profiles")
        return valid_profiles
    
    async def _build_single_profile(self, lead: BusinessLead) -> BusinessProfile:
        """Build an enriched profile for a single business lead.
        
        Args:
            lead: Business lead to enrich
            
        Returns:
            Enriched business profile
        """
        logger.debug(f"Building profile for {lead.name}")
        
        # Create base profile
        profile = BusinessProfile(lead=lead)
        
        # Enrich with data from multiple sources
        enrichment_tasks = [
            self._enrich_business_details(profile),
            self._enrich_social_media(profile),
            self._enrich_news_articles(profile),
            self._enrich_directory_listings(profile)
        ]
        
        await asyncio.gather(*enrichment_tasks, return_exceptions=True)
        
        # Calculate enrichment score
        profile.enrichment_score = self._calculate_enrichment_score(profile)
        
        return profile
    
    async def _enrich_business_details(self, profile: BusinessProfile) -> None:
        """Enrich profile with additional business details."""
        await rate_limiter.wait_for_tokens("business_details", 1)
        
        # TODO: Replace with real business data enrichment APIs
        if not settings.ENABLE_SIMULATION:
            return
        
        logger.debug(f"Enriching business details for {profile.lead.name}")
        await asyncio.sleep(0.1)  # Simulate API delay
        
        # Simulated business details
        profile.description = f"{profile.lead.name} is a leading {profile.lead.industry} business located in {profile.lead.location}."
        profile.founded_year = random.randint(1980, 2020)
        
        employee_ranges = ["1-10", "11-50", "51-200", "201-500", "500+"]
        profile.employee_count = random.choice(employee_ranges)
        
        revenue_ranges = ["$0-1M", "$1M-10M", "$10M-50M", "$50M+"]
        profile.annual_revenue = random.choice(revenue_ranges)
        
        profile.enrichment_sources.append("business_details")
    
    async def _enrich_social_media(self, profile: BusinessProfile) -> None:
        """Enrich profile with social media presence."""
        await rate_limiter.wait_for_tokens("social_media", 1)
        
        # TODO: Replace with real social media API integrations
        if not settings.ENABLE_SIMULATION:
            return
        
        logger.debug(f"Enriching social media for {profile.lead.name}")
        await asyncio.sleep(0.2)  # Simulate API delay
        
        # Simulated social media profiles
        platforms = ["linkedin", "facebook", "instagram", "twitter"]
        for platform in platforms[:random.randint(1, 3)]:
            social_profile = SocialMediaProfile(
                platform=platform,
                url=f"https://{platform}.com/{profile.lead.business_id}",
                followers=random.randint(100, 10000),
                verified=random.random() > 0.8,
                last_post=datetime.now() - timedelta(days=random.randint(1, 30)),
                engagement_rate=random.uniform(0.01, 0.1)
            )
            profile.social_profiles.append(social_profile)
        
        if profile.social_profiles:
            profile.enrichment_sources.append("social_media")
    
    async def _enrich_news_articles(self, profile: BusinessProfile) -> None:
        """Enrich profile with recent news articles."""
        await rate_limiter.wait_for_tokens("news_api", 1)
        
        # TODO: Replace with real news API integration
        if not settings.ENABLE_SIMULATION:
            return
        
        logger.debug(f"Enriching news articles for {profile.lead.name}")
        await asyncio.sleep(0.15)  # Simulate API delay
        
        # Simulated news articles
        for i in range(random.randint(0, 3)):
            article = NewsArticle(
                title=f"{profile.lead.name} {random.choice(['Expands', 'Launches', 'Announces', 'Partners with'])} {random.choice(['New Service', 'Innovation', 'Initiative', 'Local Business'])}",
                url=f"https://news-example.com/article-{random.randint(1000, 9999)}",
                published_date=datetime.now() - timedelta(days=random.randint(1, 90)),
                source=random.choice(["Local News", "Business Journal", "Industry Today"]),
                sentiment=random.choice(["positive", "neutral", "positive"])  # Bias toward positive
            )
            profile.news_articles.append(article)
        
        if profile.news_articles:
            profile.enrichment_sources.append("news_api")
    
    async def _enrich_directory_listings(self, profile: BusinessProfile) -> None:
        """Enrich profile with additional directory listings."""
        await rate_limiter.wait_for_tokens("directories", 1)
        
        # TODO: Replace with real directory scraping/API calls
        if not settings.ENABLE_SIMULATION:
            return
        
        logger.debug(f"Enriching directory listings for {profile.lead.name}")
        await asyncio.sleep(0.1)  # Simulate scraping delay
        
        # Simulated directory listings
        directories = ["better_business_bureau", "chamber_commerce", "industry_specific"]
        for directory in directories[:random.randint(1, 2)]:
            listing_data = {
                "listing_url": f"https://{directory}.com/business/{profile.lead.business_id}",
                "rating": random.uniform(3.0, 5.0),
                "accredited": random.random() > 0.6,
                "member_since": random.randint(2010, 2023)
            }
            profile.directory_listings[directory] = listing_data
        
        if profile.directory_listings:
            profile.enrichment_sources.append("directory_listings")
    
    def _calculate_enrichment_score(self, profile: BusinessProfile) -> float:
        """Calculate enrichment score based on available data.
        
        Args:
            profile: Business profile to score
            
        Returns:
            Enrichment score between 0.0 and 1.0
        """
        score = 0.0
        max_score = 1.0
        
        # Base information (20%)
        if profile.description:
            score += 0.1
        if profile.founded_year:
            score += 0.05
        if profile.employee_count:
            score += 0.05
        
        # Social media presence (30%)
        if profile.social_profiles:
            score += 0.2
            if len(profile.social_profiles) >= 3:
                score += 0.1
        
        # News coverage (25%)
        if profile.news_articles:
            score += 0.15
            if len(profile.news_articles) >= 2:
                score += 0.1
        
        # Directory listings (25%)
        if profile.directory_listings:
            score += 0.15
            if len(profile.directory_listings) >= 2:
                score += 0.1
        
        return min(score, max_score)

# TODO: Future enhancements for profile building:
# - Real API integrations for business data enrichment
# - Advanced social media analysis and sentiment scoring
# - Financial data integration (D&B, etc.)
# - Industry-specific enrichment sources
# - Image and logo extraction
# - Competitor analysis
# - Technology stack detection
# - Employee LinkedIn profile aggregation
# - Review aggregation and sentiment analysis