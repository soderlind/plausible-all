import requests
import time
import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

from ..models.data_models import APIResponse

class BaseAPIClient(ABC):
    """Base class for Plausible API clients."""
    
    def __init__(self, api_key: str, base_url: str, timeout: int = 30):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Set up session headers
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Plausible-Stats-Aggregator/1.0'
        })
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> APIResponse:
        """Make an HTTP request with retry logic."""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(max_retries + 1):
            try:
                self.logger.debug(f"Making {method} request to {url} (attempt {attempt + 1})")
                
                if method.upper() == 'GET':
                    response = self.session.get(url, params=params, timeout=self.timeout)
                elif method.upper() == 'POST':
                    response = self.session.post(url, json=data, params=params, timeout=self.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    self.logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                
                # Handle successful responses
                if response.status_code == 200:
                    return APIResponse.success_response(response.json(), response.status_code)
                
                # Handle client/server errors
                error_msg = f"HTTP {response.status_code}: {response.text}"
                if response.status_code < 500 or attempt == max_retries:
                    # Don't retry client errors or if we've exhausted retries
                    return APIResponse.error_response(error_msg, response.status_code)
                
                # Server error - retry with delay
                self.logger.warning(f"Server error on attempt {attempt + 1}: {error_msg}")
                time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                
            except requests.exceptions.Timeout:
                error_msg = f"Request timeout after {self.timeout} seconds"
                if attempt == max_retries:
                    return APIResponse.error_response(error_msg)
                self.logger.warning(f"Timeout on attempt {attempt + 1}, retrying...")
                time.sleep(retry_delay * (2 ** attempt))
                
            except requests.exceptions.ConnectionError as e:
                error_msg = f"Connection error: {str(e)}"
                if attempt == max_retries:
                    return APIResponse.error_response(error_msg)
                self.logger.warning(f"Connection error on attempt {attempt + 1}, retrying...")
                time.sleep(retry_delay * (2 ** attempt))
                
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                self.logger.error(error_msg)
                return APIResponse.error_response(error_msg)
        
        return APIResponse.error_response("Max retries exceeded")
    
    def close(self):
        """Close the session."""
        self.session.close()
