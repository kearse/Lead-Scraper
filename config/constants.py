"""Application constants."""

from typing import Dict, List

# Business categories and industry mappings
INDUSTRY_KEYWORDS: Dict[str, List[str]] = {
    "restaurants": ["restaurant", "cafe", "bistro", "diner", "eatery", "food service"],
    "retail": ["store", "shop", "boutique", "retail", "marketplace"],
    "services": ["service", "consulting", "professional", "agency"],
    "technology": ["tech", "software", "IT", "computer", "digital"],
    "healthcare": ["medical", "health", "clinic", "hospital", "pharmacy"],
    "real_estate": ["real estate", "property", "realty", "housing"],
    "automotive": ["auto", "car", "vehicle", "automotive", "garage"],
    "legal": ["law", "legal", "attorney", "lawyer", "paralegal"],
    "education": ["school", "education", "training", "academy", "university"],
    "fitness": ["gym", "fitness", "yoga", "training", "wellness"]
}

# Contact extraction patterns and scoring weights
DECISION_MAKER_TITLES: List[str] = [
    "CEO", "Chief Executive Officer", "President", "Owner", "Founder",
    "Managing Director", "General Manager", "VP", "Vice President",
    "Director", "Manager", "Principal", "Partner", "Head of"
]

EMAIL_DOMAINS_BUSINESS: List[str] = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",  # Personal (lower confidence)
    "company.com", "business.com", "corp.com"  # Business patterns (higher confidence)
]

# Export structure constants
EXPORT_FOLDERS: List[str] = [
    "google_business",
    "social_media", 
    "directories",
    "news",
    "contacts"
]

# Confidence scoring weights
CONFIDENCE_WEIGHTS: Dict[str, float] = {
    "complete_profile": 0.3,
    "multiple_sources": 0.2,
    "verified_contact": 0.2,
    "decision_maker_found": 0.15,
    "recent_activity": 0.1,
    "social_presence": 0.05
}

# Rate limiting defaults (requests per minute by source)
RATE_LIMITS: Dict[str, int] = {
    "google_places": 100,
    "yelp": 5000,
    "linkedin": 20,
    "facebook": 200,
    "instagram": 200,
    "twitter": 300,
    "news_api": 1000
}

# User agents for web scraping (when implemented)
USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]