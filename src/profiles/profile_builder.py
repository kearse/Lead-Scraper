"""Business profile building and enrichment."""

import asyncio
import random
import sys
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Add root directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.discovery.search_engine import BusinessSearchResult
from src.utils.logger import logger


@dataclass
class Contact:
    """Represents a business contact."""
    
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    source: str = "unknown"
    confidence_score: float = 0.5
    is_decision_maker: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)


@dataclass
class SocialMediaProfile:
    """Represents social media profile information."""
    
    platform: str
    url: Optional[str] = None
    followers: Optional[int] = None
    verified: bool = False
    last_updated: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)


@dataclass
class NewsArticle:
    """Represents a news article mention."""
    
    title: str
    url: Optional[str] = None
    source: Optional[str] = None
    published_date: Optional[str] = None
    summary: Optional[str] = None
    sentiment: Optional[str] = None  # positive, negative, neutral
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)


@dataclass
class BusinessProfile:
    """Complete business profile with enriched data."""
    
    # Basic information (from search)
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    
    # Enriched information
    description: Optional[str] = None
    founded_year: Optional[int] = None
    employee_count: Optional[str] = None
    annual_revenue: Optional[str] = None
    
    # Contact information
    contacts: List[Contact] = field(default_factory=list)
    
    # Social media
    social_media: List[SocialMediaProfile] = field(default_factory=list)
    
    # News mentions
    news_mentions: List[NewsArticle] = field(default_factory=list)
    
    # Metadata
    sources: List[str] = field(default_factory=list)
    confidence_score: float = 0.5
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "website": self.website,
            "industry": self.industry,
            "description": self.description,
            "founded_year": self.founded_year,
            "employee_count": self.employee_count,
            "annual_revenue": self.annual_revenue,
            "contacts": [contact.to_dict() for contact in self.contacts],
            "social_media": [sm.to_dict() for sm in self.social_media],
            "news_mentions": [article.to_dict() for article in self.news_mentions],
            "sources": self.sources,
            "confidence_score": self.confidence_score,
            "last_updated": self.last_updated
        }
    
    def get_decision_makers(self) -> List[Contact]:
        """Get contacts identified as decision makers."""
        return [contact for contact in self.contacts if contact.is_decision_maker]
    
    def get_all_emails(self) -> List[str]:
        """Get all email addresses found for this business."""
        emails = []
        for contact in self.contacts:
            if contact.email:
                emails.append(contact.email)
        return list(set(emails))  # Remove duplicates
    
    def get_all_phones(self) -> List[str]:
        """Get all phone numbers found for this business."""
        phones = []
        if self.phone:
            phones.append(self.phone)
        for contact in self.contacts:
            if contact.phone:
                phones.append(contact.phone)
        return list(set(phones))  # Remove duplicates


class ProfileBuilder:
    """Builds enriched business profiles from search results."""
    
    async def build_profile(self, search_result: BusinessSearchResult) -> BusinessProfile:
        """Build an enriched business profile from a search result."""
        logger.info(f"Building profile for: {search_result.name}")
        
        # Create base profile from search result
        profile = BusinessProfile(
            name=search_result.name,
            address=search_result.address,
            phone=search_result.phone,
            website=search_result.website,
            industry=search_result.industry,
            sources=[search_result.source],
            confidence_score=search_result.confidence_score
        )
        
        # Run enrichment tasks in parallel
        enrichment_tasks = [
            self._enrich_basic_info(profile),
            self._enrich_contacts(profile),
            self._enrich_social_media(profile),
            self._enrich_news_mentions(profile)
        ]
        
        await asyncio.gather(*enrichment_tasks, return_exceptions=True)
        
        # Update overall confidence score
        profile.confidence_score = self._calculate_confidence_score(profile)
        
        logger.info(f"Profile built for {profile.name} (confidence: {profile.confidence_score:.2f})")
        return profile
    
    async def _enrich_basic_info(self, profile: BusinessProfile) -> None:
        """Enrich basic business information (mock implementation)."""
        logger.debug(f"Enriching basic info for {profile.name}")
        
        # Simulate API delay
        await asyncio.sleep(0.2)
        
        # Mock enrichment data
        profile.description = f"A {profile.industry or 'business'} company serving the local community."
        profile.founded_year = random.randint(1990, 2020)
        profile.employee_count = random.choice(["1-10", "11-50", "51-200", "201-500"])
        profile.annual_revenue = random.choice(["<$1M", "$1M-$5M", "$5M-$10M", "$10M+"])
    
    async def _enrich_contacts(self, profile: BusinessProfile) -> None:
        """Extract and enrich contact information (mock implementation)."""
        logger.debug(f"Enriching contacts for {profile.name}")
        
        # Simulate API delay
        await asyncio.sleep(0.3)
        
        # Mock contact data
        mock_contacts = [
            Contact(
                name="John Smith",
                email=f"john.smith@{profile.name.lower().replace(' ', '')}.com",
                phone=f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}",
                title="Owner",
                department="Management",
                source="website",
                confidence_score=0.8,
                is_decision_maker=True
            ),
            Contact(
                name="Sarah Johnson", 
                email=f"sarah@{profile.name.lower().replace(' ', '')}.com",
                title="Manager",
                department="Operations",
                source="linkedin",
                confidence_score=0.6,
                is_decision_maker=True
            )
        ]
        
        # Add a subset of mock contacts
        profile.contacts = random.sample(mock_contacts, random.randint(1, len(mock_contacts)))
    
    async def _enrich_social_media(self, profile: BusinessProfile) -> None:
        """Enrich social media profile information (mock implementation)."""
        logger.debug(f"Enriching social media for {profile.name}")
        
        # Simulate API delay
        await asyncio.sleep(0.25)
        
        # Mock social media profiles
        platforms = ["LinkedIn", "Facebook", "Twitter", "Instagram"]
        
        for platform in random.sample(platforms, random.randint(1, 3)):
            social_profile = SocialMediaProfile(
                platform=platform,
                url=f"https://{platform.lower()}.com/{profile.name.lower().replace(' ', '')}",
                followers=random.randint(50, 5000),
                verified=random.choice([True, False]),
                last_updated=datetime.now().isoformat()
            )
            profile.social_media.append(social_profile)
    
    async def _enrich_news_mentions(self, profile: BusinessProfile) -> None:
        """Enrich news mentions (mock implementation)."""
        logger.debug(f"Enriching news mentions for {profile.name}")
        
        # Simulate API delay
        await asyncio.sleep(0.15)
        
        # Mock news articles (some businesses might not have any)
        if random.choice([True, False]):
            article = NewsArticle(
                title=f"{profile.name} Expands Local Operations",
                url=f"https://localnews.example.com/business/{profile.name.lower().replace(' ', '-')}",
                source="Local Business Journal",
                published_date="2023-10-15",
                summary=f"Local business {profile.name} announces expansion plans.",
                sentiment="positive"
            )
            profile.news_mentions.append(article)
    
    def _calculate_confidence_score(self, profile: BusinessProfile) -> float:
        """Calculate overall confidence score for the profile."""
        scores = []
        
        # Base score from search result
        scores.append(profile.confidence_score)
        
        # Contact information quality
        if profile.contacts:
            contact_scores = [c.confidence_score for c in profile.contacts]
            scores.append(sum(contact_scores) / len(contact_scores))
        
        # Data completeness
        completeness_factors = [
            bool(profile.address),
            bool(profile.phone),
            bool(profile.website),
            bool(profile.description),
            bool(profile.contacts),
            bool(profile.social_media)
        ]
        completeness_score = sum(completeness_factors) / len(completeness_factors)
        scores.append(completeness_score)
        
        # Return weighted average
        return sum(scores) / len(scores)