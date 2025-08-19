"""Application constants."""

# Search source types
SEARCH_SOURCES = {
    "GOOGLE_MAPS": "google_maps",
    "YELP": "yelp", 
    "YELLOW_PAGES": "yellow_pages",
    "BING_PLACES": "bing_places"
}

# Contact types
CONTACT_TYPES = {
    "EMAIL": "email",
    "PHONE": "phone",
    "WEBSITE": "website",
    "SOCIAL": "social"
}

# Decision maker roles (for scoring)
DECISION_MAKER_ROLES = [
    "CEO", "President", "Owner", "Manager", "Director", 
    "VP", "Vice President", "Chief", "Head", "Principal"
]

# File extensions
EXPORT_EXTENSIONS = {
    "json": ".json",
    "csv": ".csv", 
    "txt": ".txt"
}

# Mock data industries
MOCK_INDUSTRIES = [
    "restaurants", "retail", "professional_services", 
    "healthcare", "automotive", "real_estate",
    "technology", "construction", "education"
]

# Confidence score thresholds
CONFIDENCE_LEVELS = {
    "HIGH": 0.8,
    "MEDIUM": 0.5, 
    "LOW": 0.2
}