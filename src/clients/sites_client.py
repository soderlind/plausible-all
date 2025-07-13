import logging
from typing import List, Optional

from .base_client import BaseAPIClient
from ..models.data_models import Site, APIResponse

class SitesAPIClient(BaseAPIClient):
    """Client for Plausible Sites API."""
    
    def __init__(self, api_key: str, base_url: str, timeout: int = 30):
        super().__init__(api_key, base_url, timeout)
        self.logger = logging.getLogger(__name__)
    
    def get_sites(self, limit: int = 100) -> List[Site]:
        """
        Retrieve all sites accessible to the API key.
        
        Args:
            limit: Maximum number of sites per request (default: 100)
            
        Returns:
            List of Site objects
            
        Raises:
            Exception: If API request fails
        """
        sites = []
        after_cursor = None
        
        while True:
            params = {'limit': limit}
            if after_cursor:
                params['after'] = after_cursor
            
            self.logger.info(f"Fetching sites (limit: {limit}, after: {after_cursor})")
            response = self._make_request('GET', '/sites', params=params)
            
            if not response.success:
                error_msg = f"Failed to fetch sites: {response.error}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
            
            data = response.data
            site_data = data.get('sites', [])
            
            # Convert to Site objects
            for site_info in site_data:
                site = Site(
                    domain=site_info['domain'],
                    timezone=site_info.get('timezone', 'UTC')
                )
                sites.append(site)
                self.logger.debug(f"Added site: {site}")
            
            # Check for pagination
            meta = data.get('meta', {})
            after_cursor = meta.get('after')
            
            if not after_cursor:
                # No more pages
                break
            
            self.logger.info(f"Found {len(site_data)} sites in this batch, continuing pagination...")
        
        self.logger.info(f"Retrieved {len(sites)} total sites")
        return sites
    
    def get_site(self, domain: str) -> Optional[Site]:
        """
        Get details of a specific site.
        
        Args:
            domain: The domain of the site
            
        Returns:
            Site object if found, None otherwise
        """
        self.logger.info(f"Fetching site details for: {domain}")
        response = self._make_request('GET', f'/sites/{domain}')
        
        if not response.success:
            if response.status_code == 404:
                self.logger.warning(f"Site not found: {domain}")
                return None
            
            error_msg = f"Failed to fetch site {domain}: {response.error}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
        
        data = response.data
        site = Site(
            domain=data['domain'],
            timezone=data.get('timezone', 'UTC')
        )
        
        self.logger.debug(f"Retrieved site: {site}")
        return site
