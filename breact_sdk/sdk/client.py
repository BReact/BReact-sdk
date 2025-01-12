from typing import Dict, Optional, Type, TypeVar, Any
import os
from breact_sdk.sdk.exceptions import ServiceExecutionError, ServiceNotFoundError
from breact_sdk.sdk.types.responses import ServiceResponse
from .types.services import Service, BaseService
from ..services import ServiceRegistry, SERVICE_REGISTRY
from .utils.http import HttpClient

T = TypeVar('T', bound=BaseService)

class BReactClient:
    def __init__(
        self,
        base_url: str = "https://api-os.breact.ai",
        api_key: Optional[str] = None,
        request_timeout: int = 30,
        poll_interval: float = 3.0,
        poll_timeout: float = 180.0
    ):
        # Try environment variable first, then fall back to passed api_key
        self.api_key = os.getenv("BREACT_API_KEY") or api_key
        if not self.api_key:
            raise ValueError("API key must be provided either through BREACT_API_KEY environment variable or api_key parameter")
            
        self.base_url = base_url
        self.registry = ServiceRegistry()
        self.registry.set_client(self)
        self._service_cache: Dict[str, BaseService] = {}
        self._http = HttpClient(
            base_url,
            self.api_key,
            request_timeout,
            poll_interval,
            poll_timeout
        )
        
    async def _make_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to BReact OS API"""
        return await self._http.request(method, path, params, json)
        
    async def close(self):
        """Close the client and cleanup resources"""
        await self._http.close()
    
    async def fetch_services(self) -> Dict[str, Service]:
        """Fetch and register all available services from BReact OS"""
        response = await self._make_request("GET", "/api/v1/services")
        
        for service_data in response.values():
            self.registry.register_service_definition(service_data)
            
        return self.registry.list_services()
    
    async def get_service(self, service_id: str) -> Optional[BaseService]:
        """
        Get or create a service instance by ID.
        
        If a pre-built service implementation exists in SERVICE_REGISTRY,
        it will be used. Otherwise, a generic BaseService implementation
        will be created.
        """
        if service_id in self._service_cache:
            return self._service_cache[service_id]
            
        # Check if we have a pre-built implementation
        service_class = SERVICE_REGISTRY.get(service_id)
        if service_class:
            instance = self.register_service(service_class)
        else:
            # Create generic service implementation
            service_def = self.registry.get_service(service_id)
            if not service_def:
                return None
            instance = self._create_generic_service(service_def)
            
        await instance.initialize()
        self._service_cache[service_id] = instance
        return instance
    
    def register_service(self, service_class: Type[T]) -> T:
        """Register a custom service implementation"""
        instance = self.registry.register_service_instance(service_class)
        self._service_cache[instance.service_id] = instance
        return instance
    
    def _create_generic_service(self, service_def: Service) -> BaseService:
        """Create a generic service implementation from a service definition"""
        class GenericService(BaseService):
            service_id = service_def.id
            service_config = service_def.config
            _service_definition = service_def
            
            async def initialize(self) -> None:
                pass
                
        return self.register_service(GenericService)
    
    async def execute_service(
        self,
        service_id: str,
        endpoint: str,
        params: Dict[str, Any]
    ) -> ServiceResponse:
        """Execute a service endpoint with result polling"""
        service = self.registry.get_service(service_id)
        if not service:
            raise ServiceNotFoundError(f"Service '{service_id}' not found")
            
        path = f"/api/v1/services/{service_id}/{endpoint}"
        response = await self._http.execute_with_polling(
            "POST",
            path,
            json=params
        )
        
        if response.status == "error":
            raise ServiceExecutionError(response.error or "Unknown error")
            
        return response