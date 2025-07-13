import logging
import time
from datetime import datetime
from typing import List, Optional

from .base_client import BaseAPIClient
from ..models.data_models import SiteStats, StatsQuery, APIResponse

class StatsAPIClient(BaseAPIClient):
    """Client for Plausible Stats API."""
    
    def __init__(self, api_key: str, base_url: str, timeout: int = 30, request_delay: float = 3.6):
        super().__init__(api_key, base_url, timeout)
        self.request_delay = request_delay  # Delay between requests to respect rate limits
        self.last_request_time = 0
        self.logger = logging.getLogger(__name__)
    
    def _rate_limit_delay(self):
        """Apply rate limiting delay between requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.request_delay:
            sleep_time = self.request_delay - time_since_last_request
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def get_site_stats(self, site_domain: str, metrics: List[str], date_range: str) -> Optional[SiteStats]:
        """
        Get stats for a specific site.
        
        Args:
            site_domain: Domain of the site
            metrics: List of metrics to retrieve
            date_range: Date range ('month' or 'year')
            
        Returns:
            SiteStats object if successful, None otherwise
        """
        # Apply rate limiting
        self._rate_limit_delay()
        
        query = StatsQuery(
            site_id=site_domain,
            metrics=metrics,
            date_range=date_range
        )
        
        self.logger.info(f"Fetching {date_range} stats for site: {site_domain}")
        self.logger.debug(f"Query: {query.to_dict()}")
        
        response = self._make_request('POST', '/query', data=query.to_dict())
        
        if not response.success:
            self.logger.error(f"Failed to fetch stats for {site_domain}: {response.error}")
            return None
        
        data = response.data
        results = data.get('results', [])
        
        if not results:
            self.logger.warning(f"No stats data returned for {site_domain}")
            return None
        
        # Extract metrics from the first result (aggregated data)
        result = results[0]
        metrics_data = result.get('metrics', [])
        
        if len(metrics_data) != len(metrics):
            self.logger.warning(f"Metrics count mismatch for {site_domain}. Expected {len(metrics)}, got {len(metrics_data)}")
            return None
        
        # Map metrics to values
        metrics_dict = dict(zip(metrics, metrics_data))
        
        # Handle potential None values and convert to appropriate types
        try:
            stats = SiteStats(
                site_domain=site_domain,
                period=date_range,
                date_range=str(data.get('query', {}).get('date_range', date_range)),
                visitors=int(metrics_dict.get('visitors', 0) or 0),
                visits=int(metrics_dict.get('visits', 0) or 0),
                pageviews=int(metrics_dict.get('pageviews', 0) or 0),
                bounce_rate=float(metrics_dict.get('bounce_rate', 0.0) or 0.0),
                visit_duration=int(metrics_dict.get('visit_duration', 0) or 0),
                views_per_visit=float(metrics_dict.get('views_per_visit', 0.0) or 0.0),
                retrieved_at=datetime.now()
            )
            
            self.logger.debug(f"Created stats: {stats}")
            return stats
            
        except (ValueError, TypeError) as e:
            self.logger.error(f"Error parsing stats data for {site_domain}: {e}")
            self.logger.debug(f"Raw metrics data: {metrics_dict}")
            return None
    
    def get_bulk_stats(self, sites: List[str], metrics: List[str], date_ranges: List[str]) -> List[SiteStats]:
        """
        Get stats for multiple sites and date ranges.
        
        Args:
            sites: List of site domains
            metrics: List of metrics to retrieve
            date_ranges: List of date ranges ('month', 'year', etc.)
            
        Returns:
            List of SiteStats objects
        """
        all_stats = []
        total_requests = len(sites) * len(date_ranges)
        completed_requests = 0
        
        self.logger.info(f"Starting bulk stats collection for {len(sites)} sites and {len(date_ranges)} date ranges")
        self.logger.info(f"Total requests to make: {total_requests}")
        
        for site_domain in sites:
            for date_range in date_ranges:
                try:
                    stats = self.get_site_stats(site_domain, metrics, date_range)
                    if stats:
                        all_stats.append(stats)
                    
                    completed_requests += 1
                    if completed_requests % 10 == 0:  # Progress logging every 10 requests
                        self.logger.info(f"Progress: {completed_requests}/{total_requests} requests completed")
                        
                except Exception as e:
                    self.logger.error(f"Error getting stats for {site_domain} ({date_range}): {e}")
                    completed_requests += 1
                    continue
        
        self.logger.info(f"Bulk stats collection completed. Retrieved {len(all_stats)} stat records")
        return all_stats
