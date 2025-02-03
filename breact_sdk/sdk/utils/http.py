from typing import Optional, Dict, Any, Union, List
import httpx
from ..exceptions import BReactClientError, ServiceExecutionError
import asyncio
from ..types.responses import ServiceResponse, ProcessResponse
import logging

logger = logging.getLogger("breact_sdk.http")

class HttpClient:
    """HTTP client for making requests to BReact OS API"""
    
    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        request_timeout: int = 180,    # Timeout for generation requests (3 mins)
        poll_interval: float = 3.0,    # How often to poll
        poll_timeout: int = 30         # Timeout for polling requests (30s)
    ):
        logger.info(f"Initializing HTTP client for {base_url}")
        self.base_url = base_url.rstrip('/')
        self.request_timeout = request_timeout
        self.poll_interval = poll_interval
        self.poll_timeout = poll_timeout
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        if api_key:
            logger.debug("Setting API key header")
            # Always use x-api-key header
            self.headers["x-api-key"] = api_key
            logger.debug(f"Headers after setting API key: {self.headers}")
            
        # Use different timeouts for different types of requests
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=request_timeout
        )
        
        logger.info("HTTP client initialized successfully")
    
    async def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        is_polling: bool = False
    ) -> Dict[str, Any]:
        """Make HTTP request with error handling and response parsing"""
        logger.info(f"Making {method} request to {path}")
        logger.debug(f"Request headers: {self._client.headers}")
        logger.debug(f"Request params: {params}")
        logger.debug(f"Request body: {json}")
        
        try:
            # Use shorter timeout for polling requests
            timeout = self.poll_timeout if is_polling else self.request_timeout
            
            response = await self._client.request(
                method=method,
                url=path,
                params=params,
                json=json,
                timeout=timeout
            )
            
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {response.headers}")
            
            response.raise_for_status()
            data = response.json()
            logger.debug(f"Response data: {data}")
            return data
            
        except httpx.TimeoutException as e:
            logger.error(f"Request timed out: {str(e)}")
            raise BReactClientError(f"Request timed out: {str(e)}")
        except httpx.HTTPError as e:
            logger.error(f"HTTP request failed: {str(e)}")
            raise BReactClientError(f"HTTP request failed: {str(e)}")
    
    async def close(self):
        """Close the HTTP client session"""
        logger.info("Closing HTTP client")
        await self._client.aclose()
        logger.debug("HTTP client closed successfully")
    
    async def poll_result(
        self,
        process_id: str,
        access_token: str,
        interval: Optional[float] = None
    ) -> ServiceResponse:
        """Poll for service result until completion"""
        interval = interval or self.poll_interval
        
        while True:
            response = await self.request(
                "GET",
                f"/api/v1/services/result/{process_id}",
                params={"access_token": access_token},
                is_polling=True  # Use shorter timeout for polling
            )
            
            result = ServiceResponse.model_validate(response)
            if result.status != "pending":
                return result
                
            await asyncio.sleep(interval)
            
    async def execute_with_polling(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        interval: Optional[float] = None
    ) -> ServiceResponse:
        """Execute request and poll for result"""
        logger.info(f"Executing {method} request to {path} with polling")
        
        response = await self.request(method, path, json=json)
        process = ProcessResponse.model_validate(response)
        
        logger.debug(f"\nSubmitted request:")
        logger.debug(f"Process ID: {process.process_id}")
        logger.debug(f"Access Token: {process.access_token}")
        
        return await self.poll_result(
            process.process_id,
            process.access_token,
            interval
        )
        
    async def execute_batch(
        self,
        requests: List[Dict[str, Any]],
        interval: Optional[float] = None
    ) -> List[ServiceResponse]:
        """Execute multiple requests concurrently"""
        # Submit all requests
        tasks = []
        for req in requests:
            task = self.request(
                req["method"],
                req["path"],
                json=req.get("json")
            )
            tasks.append(task)
            
        # Wait for initial responses
        processes = await asyncio.gather(*tasks)
        
        # Create polling tasks
        poll_tasks = []
        for proc in processes:
            process = ProcessResponse.model_validate(proc)
            task = self.poll_result(
                process.process_id,
                process.access_token,
                interval
            )
            poll_tasks.append(task)
            
        # Wait for all results
        return await asyncio.gather(*poll_tasks)
