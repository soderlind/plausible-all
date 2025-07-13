import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Settings:
    """Configuration settings for the Plausible stats aggregator."""
    
    def __init__(self):
        # API Configuration
        self.sites_api_key: str = self._get_required_env("PLAUSIBLE_SITES_API_KEY")
        self.stats_api_key: str = self._get_required_env("PLAUSIBLE_STATS_API_KEY")
        self.base_url: str = os.getenv("PLAUSIBLE_BASE_URL", "https://plausible.io")
        
        # Output Configuration
        self.output_dir: str = os.getenv("OUTPUT_DIR", "./output")
        
        # Logging Configuration
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        
        # API Rate Limiting
        self.max_requests_per_hour: int = 600
        self.request_delay: float = 3.6  # Seconds between requests to stay under rate limit
        
        # Request Configuration
        self.request_timeout: int = 30
        self.max_retries: int = 3
        self.retry_delay: float = 1.0
        
        # Metrics to collect
        self.metrics: list = [
            "visitors",
            "visits", 
            "pageviews",
            "bounce_rate",
            "visit_duration",
            "views_per_visit"
        ]
    
    def _get_required_env(self, key: str) -> str:
        """Get required environment variable or raise error."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    @property
    def sites_api_url(self) -> str:
        """Get the Sites API base URL."""
        return f"{self.base_url}/api/v1"
    
    @property
    def stats_api_url(self) -> str:
        """Get the Stats API base URL."""
        return f"{self.base_url}/api/v2"
    
    def validate(self) -> None:
        """Validate configuration settings."""
        if not self.sites_api_key.strip():
            raise ValueError("Sites API key cannot be empty")
        
        if not self.stats_api_key.strip():
            raise ValueError("Stats API key cannot be empty")
        
        if not self.base_url.startswith(('http://', 'https://')):
            raise ValueError("Base URL must start with http:// or https://")

# Global settings instance
settings = Settings()
