import os
import time
import asyncio
import httpx
import logging
from typing import Any, Dict, Optional, Union
from .config import Configuration

# Set up logging with default level
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceProxy:
    """A proxy class that allows dynamic access to service endpoints."""
    def __init__(self, client, service_id: str):
        self._client = client
        self._service_id = service_id

    def __getattr__(self, endpoint: str) -> callable:
        """
        Dynamically create a method for the requested endpoint.
        This allows users to call endpoints like: client.service_name.endpoint_name(params)
        """
        async def _async_execute(**params):
            return await self._client.execute_service(self._service_id, endpoint, params)

        def _sync_execute(**params):
            return self._client.execute_service(self._service_id, endpoint, params)

        # Return async or sync version based on client type
        return _async_execute if isinstance(self._client, AsyncBReactClient) else _sync_execute

class AsyncBReactClient:
    def __init__(self, api_key: str = None, base_url: str = None):
        """
        Initialize the asynchronous BReact client.

        :param api_key: API key; if not provided, use the one from config
        :param base_url: Base URL for the API; if not provided, use the one from config
        """
        self.config = Configuration(api_key=api_key, base_url=base_url)
        self.client = httpx.AsyncClient(
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.config.api_key,
            }
        )
        self._service_cache = {}

    def __getattr__(self, service_id: str) -> ServiceProxy:
        """
        Dynamically create a ServiceProxy for the requested service.
        This allows users to access services like: client.service_name
        """
        if service_id not in self._service_cache:
            self._service_cache[service_id] = ServiceProxy(self, service_id)
        return self._service_cache[service_id]

    @property
    def services(self):
        """Access service listing functionality."""
        return self

    async def list(self) -> dict:
        """
        List all available services.

        :return: Dictionary containing available services
        """
        url = f"{self.config.api_base_url}/services"
        logger.debug(f"Making request to {url}")
        
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def execute_service(
        self,
        service_id: str,
        endpoint: str,
        params: dict,
        wait_for_result: bool = True,
        poll_interval: Optional[float] = None,
        timeout: Optional[float] = None,
    ) -> dict:
        """
        Execute a service call and optionally poll for the final result.

        :param service_id: The service identifier (e.g., "information_tracker")
        :param endpoint: The endpoint to call (e.g., "process")
        :param params: Request payload (including content, context, config, etc.)
        :param wait_for_result: If True, automatically poll until the result is ready
        :param poll_interval: Seconds between polls (overrides config value)
        :param timeout: Maximum seconds to wait for completion (overrides config value)
        :return: The final result data, or process details if wait_for_result is False
        """
        url = f"{self.config.api_base_url}/services/{service_id}/{endpoint}"
        logger.debug(f"Making request to {url} with params: {params}")
        
        response = await self.client.post(url, json=params)
        response.raise_for_status()
        data = response.json()
        logger.debug(f"Initial response: {data}")

        process_id = data.get("process_id")
        access_token = data.get("access_token")
        if not process_id or not access_token:
            # If no process_id/access_token, this might be a direct response
            if "result" in data:
                return data["result"]
            if "data" in data:
                return data["data"]
            return data

        if not wait_for_result:
            return {"process_id": process_id, "access_token": access_token}

        return await self.poll_result(
            process_id, 
            access_token, 
            poll_interval or self.config.poll_interval,
            timeout or self.config.timeout
        )

    async def poll_result(
        self,
        process_id: str,
        access_token: str,
        poll_interval: float = None,
        timeout: float = None,
    ) -> dict:
        """
        Poll the results endpoint until the service is complete.

        :param process_id: The process identifier
        :param access_token: The access token
        :param poll_interval: Seconds between polls (overrides config value)
        :param timeout: Maximum seconds to wait (overrides config value)
        :return: The final result data
        :raises TimeoutError: if polling times out
        """
        start_time = time.time()
        poll_url = f"{self.config.api_base_url}/services/result/{process_id}?access_token={access_token}"
        logger.debug(f"Polling URL: {poll_url}")

        poll_interval = poll_interval or self.config.poll_interval
        timeout = timeout or self.config.timeout

        while True:
            response = await self.client.get(poll_url)
            response.raise_for_status()
            result = response.json()
            logger.debug(f"Poll response: {result}")

            if result.get("status") == "completed":
                if "result" in result:
                    return result["result"]
                if "data" in result:
                    return result["data"]
                return result

            if time.time() - start_time > timeout:
                raise TimeoutError("Polling timed out waiting for the result.")

            await asyncio.sleep(poll_interval)

    async def close(self):
        """Close the asynchronous HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Support async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Support async context manager."""
        await self.close()

class SyncBReactClient:
    def __init__(self, api_key: str = None, base_url: str = None):
        """
        Initialize the synchronous BReact client.

        :param api_key: API key; if not provided, use the one from config
        :param base_url: Base URL for the API; if not provided, use the one from config
        """
        self.config = Configuration(api_key=api_key, base_url=base_url)
        self.client = httpx.Client(
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.config.api_key,
            }
        )
        self._service_cache = {}

    def __getattr__(self, service_id: str) -> ServiceProxy:
        """
        Dynamically create a ServiceProxy for the requested service.
        This allows users to access services like: client.service_name
        """
        if service_id not in self._service_cache:
            self._service_cache[service_id] = ServiceProxy(self, service_id)
        return self._service_cache[service_id]

    @property
    def services(self):
        """Access service listing functionality."""
        return self

    def list(self) -> dict:
        """
        List all available services.

        :return: Dictionary containing available services
        """
        url = f"{self.config.api_base_url}/services"
        logger.debug(f"Making request to {url}")
        
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()

    def execute_service(
        self,
        service_id: str,
        endpoint: str,
        params: dict,
        wait_for_result: bool = True,
        poll_interval: Optional[float] = None,
        timeout: Optional[float] = None,
    ) -> dict:
        """
        Execute a service call and optionally poll for the final result synchronously.

        :param service_id: The service identifier (e.g., "information_tracker")
        :param endpoint: The endpoint to call (e.g., "process")
        :param params: Request payload
        :param wait_for_result: If True, block until the final result is obtained
        :param poll_interval: Seconds between polls (overrides config value)
        :param timeout: Maximum seconds to wait for the result (overrides config value)
        :return: Final result data, or process details if wait_for_result is False
        """
        url = f"{self.config.api_base_url}/services/{service_id}/{endpoint}"
        logger.debug(f"Making request to {url} with params: {params}")
        
        response = self.client.post(url, json=params)
        response.raise_for_status()
        data = response.json()
        logger.debug(f"Initial response: {data}")

        process_id = data.get("process_id")
        access_token = data.get("access_token")
        if not process_id or not access_token:
            # If no process_id/access_token, this might be a direct response
            if "result" in data:
                return data["result"]
            if "data" in data:
                return data["data"]
            return data

        if not wait_for_result:
            return {"process_id": process_id, "access_token": access_token}

        return self.poll_result(
            process_id, 
            access_token, 
            poll_interval or self.config.poll_interval,
            timeout or self.config.timeout
        )

    def poll_result(
        self,
        process_id: str,
        access_token: str,
        poll_interval: float = None,
        timeout: float = None,
    ) -> dict:
        """
        Synchronously poll the results endpoint until processing is complete.

        :param process_id: The process identifier
        :param access_token: The access token
        :param poll_interval: Seconds between polls (overrides config value)
        :param timeout: Maximum seconds to wait for completion (overrides config value)
        :return: The final result data
        :raises TimeoutError: if the result is not available within the timeout
        """
        start_time = time.time()
        poll_url = f"{self.config.api_base_url}/services/result/{process_id}?access_token={access_token}"
        logger.debug(f"Polling URL: {poll_url}")

        poll_interval = poll_interval or self.config.poll_interval
        timeout = timeout or self.config.timeout

        while True:
            response = self.client.get(poll_url)
            response.raise_for_status()
            result = response.json()
            logger.debug(f"Poll response: {result}")

            if result.get("status") == "completed":
                if "result" in result:
                    return result["result"]
                if "data" in result:
                    return result["data"]
                return result

            if time.time() - start_time > timeout:
                raise TimeoutError("Polling timed out waiting for the result.")

            time.sleep(poll_interval)

    def close(self):
        """Close the synchronous HTTP client."""
        self.client.close()

    def __enter__(self):
        """Support context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support context manager."""
        self.close()

# Convenience function to create the appropriate client based on context
def create_client(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    async_client: bool = False
) -> Union[AsyncBReactClient, SyncBReactClient]:
    """
    Create a BReact client instance.

    :param api_key: Optional API key (overrides config and env var)
    :param base_url: Base URL for the API (overrides config and env var)
    :param async_client: If True, return an AsyncBReactClient, otherwise return a SyncBReactClient
    :return: A configured client instance
    """
    client_class = AsyncBReactClient if async_client else SyncBReactClient
    return client_class(api_key=api_key, base_url=base_url)
