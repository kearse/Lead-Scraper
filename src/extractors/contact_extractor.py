"""Contact extraction and decision maker identification."""

import asyncio
import random
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from profiles.profile_builder import BusinessProfile
from utils.logger import logger
from utils.rate_limiter import rate_limiter
from config.constants import DECISION_MAKER_TITLES
from config.settings import settings

@dataclass
class Contact:
    """Represents an extracted contact."""
    
    name: str
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    
    # Confidence and scoring
    confidence_score: float = 0.0
    decision_maker_score: float = 0.0
    
    # Source information
    source: str = ""
    extracted_at: datetime = field(default_factory=datetime.now)
    raw_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContactExtractionResult:
    """Results of contact extraction for a business."""
    
    business_name: str
    business_id: str
    
    # All extracted contacts
    all_contacts: List[Contact] = field(default_factory=list)
    
    # Decision makers (high-scoring contacts)
    decision_makers: List[Contact] = field(default_factory=list)
    
    # Extraction metadata
    extraction_score: float = 0.0
    extracted_at: datetime = field(default_factory=datetime.now)
    sources_used: List[str] = field(default_factory=list)

class ContactExtractor:
    """Extracts contacts and identifies decision makers from business profiles."""
    
    def __init__(self):
        self.decision_maker_threshold = 0.6  # Minimum score to be considered decision maker
    
    async def extract_contacts(self, profiles: List[BusinessProfile]) -> List[ContactExtractionResult]:
        """Extract contacts from business profiles.
        
        Args:
            profiles: List of business profiles to extract contacts from
            
        Returns:
            List of contact extraction results
        """
        logger.info(f"Extracting contacts from {len(profiles)} business profiles")
        
        # Process profiles concurrently
        tasks = [self._extract_single_business_contacts(profile) for profile in profiles]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out any errors
        valid_results = []
        for result in results:
            if isinstance(result, ContactExtractionResult):
                valid_results.append(result)
            else:
                logger.warning(f"Contact extraction error: {result}")
        
        logger.info(f"Successfully extracted contacts from {len(valid_results)} businesses")
        return valid_results
    
    async def _extract_single_business_contacts(self, profile: BusinessProfile) -> ContactExtractionResult:
        """Extract contacts from a single business profile.
        
        Args:
            profile: Business profile to extract contacts from
            
        Returns:
            Contact extraction result
        """
        logger.debug(f"Extracting contacts for {profile.lead.name}")
        
        # Create result container
        result = ContactExtractionResult(
            business_name=profile.lead.name,
            business_id=profile.lead.business_id
        )
        
        # Extract contacts from multiple sources
        extraction_tasks = [
            self._extract_from_website(profile, result),
            self._extract_from_social_media(profile, result),
            self._extract_from_directories(profile, result),
            self._extract_from_news(profile, result)
        ]
        
        await asyncio.gather(*extraction_tasks, return_exceptions=True)
        
        # Score decision makers
        self._score_decision_makers(result)
        
        # Calculate overall extraction score
        result.extraction_score = self._calculate_extraction_score(result)
        
        return result
    
    async def _extract_from_website(self, profile: BusinessProfile, result: ContactExtractionResult) -> None:
        """Extract contacts from business website."""
        if not profile.lead.website:
            return
        
        await rate_limiter.wait_for_tokens("website_scraping", 1)
        
        # TODO: Replace with real website scraping
        if not settings.ENABLE_SIMULATION:
            return
        
        logger.debug(f"Extracting contacts from website: {profile.lead.website}")
        await asyncio.sleep(0.2)  # Simulate scraping delay
        
        # Simulated website contact extraction
        for i in range(random.randint(1, 3)):
            contact = Contact(
                name=f"{random.choice(['John', 'Jane', 'Mike', 'Sarah', 'David', 'Lisa'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Davis', 'Miller'])}",
                title=random.choice([
                    "General Manager", "Operations Manager", "Owner", 
                    "Sales Manager", "Marketing Director", "Customer Service Manager"
                ]),
                email=self._generate_business_email(profile.lead.name),
                phone=profile.lead.phone,
                source="website",
                confidence_score=random.uniform(0.6, 0.9),
                raw_data={"url": profile.lead.website, "extraction_method": "contact_page"}
            )
            result.all_contacts.append(contact)
        
        if result.all_contacts:
            result.sources_used.append("website")
    
    async def _extract_from_social_media(self, profile: BusinessProfile, result: ContactExtractionResult) -> None:
        """Extract contacts from social media profiles."""
        if not profile.social_profiles:
            return
        
        await rate_limiter.wait_for_tokens("social_media", 1)
        
        # TODO: Replace with real social media API integrations
        if not settings.ENABLE_SIMULATION:
            return
        
        logger.debug(f"Extracting contacts from social media profiles")
        await asyncio.sleep(0.3)  # Simulate API delay
        
        # Simulated social media contact extraction
        for social_profile in profile.social_profiles[:2]:  # Limit to avoid too many contacts
            if social_profile.platform == "linkedin":
                # LinkedIn tends to have more decision makers
                contact = Contact(
                    name=f"{random.choice(['Michael', 'Jennifer', 'Robert', 'Patricia', 'William', 'Linda'])} {random.choice(['Anderson', 'Taylor', 'Thomas', 'Jackson', 'White', 'Harris'])}",
                    title=random.choice([
                        "CEO", "President", "VP of Sales", "Director of Operations",
                        "Founder", "Managing Director", "Business Development Manager"
                    ]),
                    linkedin_url=social_profile.url,
                    email=self._generate_business_email(profile.lead.name),
                    source="linkedin",
                    confidence_score=random.uniform(0.7, 0.95),
                    raw_data={"platform": "linkedin", "profile_url": social_profile.url}
                )
                result.all_contacts.append(contact)
        
        if any(sp.platform == "linkedin" for sp in profile.social_profiles):
            result.sources_used.append("social_media")
    
    async def _extract_from_directories(self, profile: BusinessProfile, result: ContactExtractionResult) -> None:
        """Extract contacts from business directory listings."""
        if not profile.directory_listings:
            return
        
        await rate_limiter.wait_for_tokens("directories", 1)
        
        # TODO: Replace with real directory scraping
        if not settings.ENABLE_SIMULATION:
            return
        
        logger.debug(f"Extracting contacts from directory listings")
        await asyncio.sleep(0.1)  # Simulate scraping delay
        
        # Simulated directory contact extraction
        if "better_business_bureau" in profile.directory_listings:
            contact = Contact(
                name=f"{random.choice(['Chris', 'Alex', 'Jordan', 'Taylor', 'Casey', 'Morgan'])} {random.choice(['Wilson', 'Moore', 'Clark', 'Lewis', 'Walker', 'Hall'])}",
                title=random.choice([
                    "Business Owner", "Manager", "Director", "Principal"
                ]),
                phone=profile.lead.phone,
                source="better_business_bureau",
                confidence_score=random.uniform(0.5, 0.8),
                raw_data={"directory": "better_business_bureau"}
            )
            result.all_contacts.append(contact)
            result.sources_used.append("directories")
    
    async def _extract_from_news(self, profile: BusinessProfile, result: ContactExtractionResult) -> None:
        """Extract contacts mentioned in news articles."""
        if not profile.news_articles:
            return
        
        await rate_limiter.wait_for_tokens("news_analysis", 1)
        
        # TODO: Replace with real news article NLP processing
        if not settings.ENABLE_SIMULATION:
            return
        
        logger.debug(f"Extracting contacts from news articles")
        await asyncio.sleep(0.15)  # Simulate NLP processing delay
        
        # Simulated news contact extraction
        for article in profile.news_articles[:1]:  # Limit to one article
            if random.random() > 0.5:  # 50% chance of finding contact in news
                contact = Contact(
                    name=f"{random.choice(['Executive', 'Spokesperson', 'Owner'])} {random.choice(['Thompson', 'Garcia', 'Martinez', 'Robinson', 'Rodriguez', 'Young'])}",
                    title=random.choice([
                        "CEO", "Founder", "President", "Spokesperson"
                    ]),
                    source="news_article",
                    confidence_score=random.uniform(0.4, 0.7),
                    raw_data={"article_title": article.title, "article_url": article.url}
                )
                result.all_contacts.append(contact)
        
        if result.all_contacts and result.sources_used and result.sources_used[-1] != "news_analysis":
            result.sources_used.append("news_analysis")
    
    def _generate_business_email(self, business_name: str) -> str:
        """Generate a plausible business email address."""
        # Clean business name for domain
        domain_name = re.sub(r'[^a-zA-Z0-9]', '', business_name.lower())[:10]
        domain = f"{domain_name}.com"
        
        # Generate email prefix
        prefixes = ["info", "contact", "sales", "admin", "office"]
        prefix = random.choice(prefixes)
        
        return f"{prefix}@{domain}"
    
    def _score_decision_makers(self, result: ContactExtractionResult) -> None:
        """Score contacts as potential decision makers."""
        for contact in result.all_contacts:
            score = 0.0
            
            # Title-based scoring
            if contact.title:
                title_lower = contact.title.lower()
                for dm_title in DECISION_MAKER_TITLES:
                    if dm_title.lower() in title_lower:
                        score += 0.4
                        break
                
                # Additional title scoring
                if any(word in title_lower for word in ["manager", "director", "head"]):
                    score += 0.2
                if any(word in title_lower for word in ["senior", "lead", "principal"]):
                    score += 0.1
            
            # Source-based scoring
            source_scores = {
                "linkedin": 0.3,
                "website": 0.2,
                "news_article": 0.2,
                "better_business_bureau": 0.1
            }
            score += source_scores.get(contact.source, 0.0)
            
            # Contact completeness scoring
            if contact.email:
                score += 0.1
            if contact.phone:
                score += 0.05
            if contact.linkedin_url:
                score += 0.1
            
            contact.decision_maker_score = min(score, 1.0)
        
        # Identify decision makers
        result.decision_makers = [
            contact for contact in result.all_contacts
            if contact.decision_maker_score >= self.decision_maker_threshold
        ]
        
        # Sort by decision maker score
        result.decision_makers.sort(key=lambda x: x.decision_maker_score, reverse=True)
    
    def _calculate_extraction_score(self, result: ContactExtractionResult) -> float:
        """Calculate overall contact extraction score.
        
        Args:
            result: Contact extraction result
            
        Returns:
            Score between 0.0 and 1.0
        """
        score = 0.0
        
        # Base score for having contacts
        if result.all_contacts:
            score += 0.3
        
        # Score for decision makers
        if result.decision_makers:
            score += 0.4
            if len(result.decision_makers) >= 2:
                score += 0.1
        
        # Score for contact completeness
        complete_contacts = sum(
            1 for contact in result.all_contacts
            if contact.email and contact.title
        )
        if complete_contacts > 0:
            score += 0.2
        
        # Score for source diversity
        if len(result.sources_used) >= 2:
            score += 0.1
        
        return min(score, 1.0)

# TODO: Future enhancements for contact extraction:
# - Real website scraping with advanced parsing
# - LinkedIn Sales Navigator integration
# - Email pattern inference and validation
# - Phone number verification and formatting
# - Advanced NLP for news article processing
# - GDPR-compliant data collection practices
# - Contact enrichment with additional data sources
# - Duplicate contact detection and merging
# - Contact verification and validation workflows