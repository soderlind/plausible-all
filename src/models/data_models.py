from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class Site:
    """Represents a Plausible site."""
    domain: str
    timezone: str
    
    def __str__(self) -> str:
        return f"Site(domain={self.domain}, timezone={self.timezone})"

@dataclass
class SiteStats:
    """Represents analytics stats for a site."""
    site_domain: str
    period: str  # 'month' or 'year'
    date_range: str  # The actual date range used
    visitors: int
    visits: int
    pageviews: int
    bounce_rate: float
    visit_duration: int
    views_per_visit: float
    retrieved_at: datetime
    
    def __str__(self) -> str:
        return f"SiteStats(site={self.site_domain}, period={self.period}, visitors={self.visitors})"

@dataclass
class APIResponse:
    """Generic API response wrapper."""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    
    @classmethod
    def success_response(cls, data: dict, status_code: int = 200) -> 'APIResponse':
        """Create a successful response."""
        return cls(success=True, data=data, status_code=status_code)
    
    @classmethod
    def error_response(cls, error: str, status_code: Optional[int] = None) -> 'APIResponse':
        """Create an error response."""
        return cls(success=False, error=error, status_code=status_code)

@dataclass
class StatsQuery:
    """Represents a stats API query."""
    site_id: str
    metrics: List[str]
    date_range: str
    dimensions: Optional[List[str]] = None
    filters: Optional[List] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API request."""
        query = {
            "site_id": self.site_id,
            "metrics": self.metrics,
            "date_range": self.date_range
        }
        
        if self.dimensions:
            query["dimensions"] = self.dimensions
            
        if self.filters:
            query["filters"] = self.filters
            
        return query
