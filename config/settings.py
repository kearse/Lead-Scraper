"""Application settings and configuration."""

import os
from typing import Dict, Any

class Settings:
    """Application settings loaded from environment variables."""
    
    # API Keys (placeholders for future integrations)
    GOOGLE_PLACES_API_KEY: str = os.getenv("GOOGLE_PLACES_API_KEY", "")
    YELP_API_KEY: str = os.getenv("YELP_API_KEY", "")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    
    # Redis/Cache settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Proxy settings
    HTTP_PROXY: str = os.getenv("HTTP_PROXY", "")
    HTTPS_PROXY: str = os.getenv("HTTPS_PROXY", "")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Rate limiting (requests per minute)
    DEFAULT_RATE_LIMIT: int = 60
    
    # Export settings
    EXPORT_BASE_DIR: str = "exports"
    
    # Simulation settings (for mock data)
    ENABLE_SIMULATION: bool = True  # TODO: Set to False when real APIs are integrated
    
    @classmethod
    def get_proxy_config(cls) -> Dict[str, str]:
        """Get proxy configuration if available."""
        config = {}
        if cls.HTTP_PROXY:
            config["http"] = cls.HTTP_PROXY
        if cls.HTTPS_PROXY:
            config["https"] = cls.HTTPS_PROXY
        return config

# Global settings instance
settings = Settings()