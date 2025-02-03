from typing import TYPE_CHECKING, Dict, Any, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
if TYPE_CHECKING:
    from ..client import BReactClient

class ParameterDefinition(BaseModel):
    type: str
    description: str
    required: bool = False
    default: Optional[Any] = None
    properties: Optional[Dict[str, Any]] = None
    items: Optional[Dict[str, Any]] = None
    enum: Optional[List[str]] = None

class EndpointReturn(BaseModel):
    type: str
    description: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None

class Endpoint(BaseModel):
    name: str
    description: str
    method: str
    parameters: Dict[str, ParameterDefinition]
    returns: Dict[str, Any]
    is_async: bool = True

class ServiceConfig(BaseModel):
    """Configuration for a service."""
    default_model: Optional[str] = None
    validation: Optional[Dict[str, Any]] = None
    default_tier: Optional[str] = None
    default_purpose: Optional[str] = None
    max_input_length: Optional[int] = None
    max_text_length: Optional[int] = None
    default_summary_length: Optional[int] = None

class Service(BaseModel):
    """Model representing a BReact OS service."""
    id: str
    name: str
    description: str
    version: str
    author: str
    path: str
    endpoints: Dict[str, Endpoint]
    config: ServiceConfig
    status: str
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class BaseService(ABC):
    """Base class for all services."""
    
    service_id: str
    service_config: ServiceConfig
    _service_definition: Optional[Service] = None

    def __init__(self, client: 'BReactClient'):
        self._client = client
        
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the service."""
        pass

    async def execute(self, endpoint: str, params: Dict[str, Any]) -> Any:
        """Execute a service endpoint with parameter validation."""
        if not self._service_definition:
            raise ValueError(f"Service definition not found for {self.service_id}")
            
        if endpoint not in self._service_definition.endpoints:
            raise ValueError(f"Unknown endpoint '{endpoint}' for service {self.service_id}")
            
        endpoint_def = self._service_definition.endpoints[endpoint]
        self._validate_parameters(endpoint_def, params)
        
        # Make the HTTP request directly instead of going through execute_service
        path = f"/api/v1/services/{self.service_id}/{endpoint}"
        return await self._client._http.execute_with_polling("POST", path, json=params)
        
    def _validate_parameters(self, endpoint: Endpoint, params: Dict[str, Any]) -> None:
        """Validate parameters against endpoint definition."""
        for param_name, param_def in endpoint.parameters.items():
            if param_def.required and param_name not in params:
                raise ValueError(f"Missing required parameter '{param_name}'")