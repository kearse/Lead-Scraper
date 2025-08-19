"""Application settings and configuration."""

import os
from pathlib import Path

class Settings:
    """Application configuration settings."""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    EXPORTS_DIR = BASE_DIR / "exports"
    
    # Default search parameters
    DEFAULT_SEARCH_LIMIT = 10
    DEFAULT_CONFIDENCE_THRESHOLD = 0.5
    
    # Export formats
    EXPORT_FORMATS = ["json", "csv", "txt"]
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Mock data settings (for initial scaffold)
    USE_MOCK_DATA = True
    MOCK_BUSINESS_COUNT = 5
    
    @classmethod
    def get_export_path(cls, campaign_name: str) -> Path:
        """Get the export path for a campaign."""
        return cls.EXPORTS_DIR / campaign_name
    
    @classmethod
    def ensure_exports_dir(cls) -> None:
        """Ensure the exports directory exists."""
        cls.EXPORTS_DIR.mkdir(exist_ok=True)

# Global settings instance
settings = Settings()