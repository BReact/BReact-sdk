from typing import Dict, Any, Optional, List, TYPE_CHECKING

from ..sdk.types.services import BaseService, ServiceConfig
from ..sdk.types.responses import ServiceResponse
from ..sdk.utils.http import HttpClient

if TYPE_CHECKING:
    from ..sdk.client import BReactClient


class InformationTrackerService(BaseService):
    """Service for tracking and analyzing information with flexible schema support."""
    
    service_id = "information_tracker"
    service_config = ServiceConfig()
    
    def __init__(self, client: 'BReactClient'):
        """Initialize the service with a client reference."""
        super().__init__(client)
        self._http_client = client._http

    async def initialize(self) -> None:
        """Initialize the service. Required by BaseService."""
        pass

    async def extract_information(
        self,
        text: str,
        schema: Dict[str, Any],
        update_type: Optional[str] = None,
        current_info: Optional[Dict[str, Any]] = None,
        model_id: Optional[str] = None,
    ) -> ServiceResponse:
        """
        Extract structured information from text based on a provided JSON schema.
        
        Args:
            text (str): The text to analyze
            schema (Dict[str, Any]): JSON schema defining the structure and constraints of the output
            update_type (Optional[str]): Type of entity being updated (e.g., "person", "company")
            current_info (Optional[Dict[str, Any]]): Currently known information about the entity
            model_id (Optional[str]): Specific model to use for extraction
            
        Returns:
            ServiceResponse: The extracted information result
        """
        params = {
            "text": text,
            "schema": schema,
            "update_type": update_type,
            "current_info": current_info,
            "model_id": model_id
        }

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        # Execute the request with polling
        result = await self._http_client.execute_with_polling(
            "POST",
            f"/api/v1/services/{self.service_id}/extract_information",
            json=params
        )

        return result 