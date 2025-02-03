from typing import Dict, Optional, Type, TypeVar, TYPE_CHECKING
from ..sdk.types.services import Service, BaseService
from .summarization import SummarizationService
from .target_analyzer import TargetAnalyzerService
from .information_tracker import InformationTrackerService

if TYPE_CHECKING:
    from ..sdk.client import BReactClient

T = TypeVar('T', bound=BaseService)

class ServiceRegistry:
    def __init__(self):
        self._services: Dict[str, Service] = {}
        self._service_instances: Dict[str, BaseService] = {}
        self._client = None
        
    def set_client(self, client: 'BReactClient') -> None:
        """Set the client reference for service instantiation"""
        self._client = client
        
    def register_service_definition(self, service_data: dict) -> Service:
        """Register a service from API response data"""
        service = Service.model_validate(service_data)
        self._services[service.id] = service
        return service
    
    def register_service_instance(self, service_class: Type[T]) -> T:
        """Register a service implementation"""
        if not self._client:
            raise ValueError("Client reference not set. Call set_client() first.")
            
        instance = service_class(client=self._client)
        if instance.service_id in self._services:
            instance._service_definition = self._services[instance.service_id]
        self._service_instances[instance.service_id] = instance
        return instance
    
    def get_service(self, service_id: str) -> Optional[Service]:
        """Get service definition by ID"""
        return self._services.get(service_id)
    
    def get_service_instance(self, service_id: str) -> Optional[BaseService]:
        """Get service implementation by ID"""
        return self._service_instances.get(service_id)
    
    def list_services(self) -> Dict[str, Service]:
        """List all registered services"""
        return self._services.copy()

SERVICE_REGISTRY: Dict[str, Type[BaseService]] = {
    "aisummary": SummarizationService,
    "target_analyzer": TargetAnalyzerService,
    "information_tracker": InformationTrackerService,
} 