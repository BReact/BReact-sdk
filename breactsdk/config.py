"""
BReact SDK Configuration Module.
Provides central configuration management for the SDK.
"""

import os
import logging
from typing import Optional, Union
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

class Configuration:
    """Central configuration class for the BReact SDK."""
    
    # Default values
    DEFAULT_BASE_URL = "https://api-os.breact.ai"
    DEFAULT_API_VERSION = "v1"
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_POLL_INTERVAL = 1.0
    DEFAULT_LOG_LEVEL = logging.INFO
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        api_version: Optional[str] = None,
        timeout: Optional[float] = None,
        poll_interval: Optional[float] = None,
        log_level: Optional[Union[int, str]] = None
    ):
        """
        Initialize SDK configuration.
        
        :param api_key: API key for authentication
        :param base_url: Base URL for the API
        :param api_version: API version to use
        :param timeout: Default timeout for requests
        :param poll_interval: Default polling interval
        :param log_level: Logging level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        """
        self.api_key = api_key or os.getenv("BREACT_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided either through constructor or BREACT_API_KEY environment variable")
        
        # Allow environment variables to override defaults
        self.base_url = (
            base_url or 
            os.getenv("BREACT_BASE_URL") or 
            self.DEFAULT_BASE_URL
        ).rstrip("/")
        
        self.api_version = (
            api_version or 
            os.getenv("BREACT_API_VERSION") or 
            self.DEFAULT_API_VERSION
        )
        
        self.timeout = float(
            timeout or 
            os.getenv("BREACT_TIMEOUT") or 
            self.DEFAULT_TIMEOUT
        )
        
        self.poll_interval = float(
            poll_interval or 
            os.getenv("BREACT_POLL_INTERVAL") or 
            self.DEFAULT_POLL_INTERVAL
        )

        # Handle log level configuration
        self.log_level = self._parse_log_level(
            log_level or 
            os.getenv("BREACT_LOG_LEVEL") or 
            self.DEFAULT_LOG_LEVEL
        )
    
    def _parse_log_level(self, level: Union[int, str]) -> int:
        """Convert string log level to logging constant if necessary."""
        if isinstance(level, int):
            return level
        try:
            return getattr(logging, level.upper())
        except (AttributeError, TypeError):
            raise ValueError(f"Invalid log level: {level}")
    
    @property
    def api_base_url(self) -> str:
        """Get the complete base URL including API version."""
        return f"{self.base_url}/api/{self.api_version}"
    
    def update(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        api_version: Optional[str] = None,
        timeout: Optional[float] = None,
        poll_interval: Optional[float] = None,
        log_level: Optional[Union[int, str]] = None
    ) -> None:
        """
        Update configuration values.
        
        :param api_key: New API key
        :param base_url: New base URL
        :param api_version: New API version
        :param timeout: New timeout value
        :param poll_interval: New polling interval
        :param log_level: New logging level
        """
        if api_key is not None:
            self.api_key = api_key
        if base_url is not None:
            self.base_url = base_url.rstrip("/")
        if api_version is not None:
            self.api_version = api_version
        if timeout is not None:
            self.timeout = float(timeout)
        if poll_interval is not None:
            self.poll_interval = float(poll_interval)
        if log_level is not None:
            self.log_level = self._parse_log_level(log_level) 