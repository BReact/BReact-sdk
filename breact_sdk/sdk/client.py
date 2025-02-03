from typing import Dict, Optional, Type, TypeVar, Any, List
import os
import logging
import asyncio
from urllib.parse import urljoin

from breact_sdk.sdk.exceptions import (
    BReactError,
    BReactClientError,
    ServiceExecutionError,
    ServiceNotFoundError
)
from breact_sdk.sdk.types.responses import ServiceResponse
from .types.services import Service, BaseService
from ..services import ServiceRegistry, SERVICE_REGISTRY
from .utils.http import HttpClient

# Set up logging
logger = logging.getLogger("breact_sdk")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

T = TypeVar('T', bound=BaseService)

class BReactClient:
    def __init__(
        self,
        base_url: str = "https://api-os.breact.ai",
        api_key: Optional[str] = None,
        request_timeout: int = 30,
        poll_interval: float = 1.0,
        poll_timeout: float = 180.0
    ):
        """Initialize client properties but don't connect yet"""
        logger.info("Initializing BReactClient...")
        self.api_key = os.getenv("BREACT_API_KEY") or api_key
        if not self.api_key:
            logger.error("No API key provided")
            raise ValueError("API key must be provided either through BREACT_API_KEY environment variable or api_key parameter")
            
        self.base_url = base_url
        self._request_timeout = request_timeout
        self._poll_interval = poll_interval
        self._poll_timeout = poll_timeout
        self._initialized = False
        self._services: Dict[str, BaseService] = {}
        
        logger.info(f"Initializing HTTP client with base URL: {base_url}")
        # Initialize HTTP client immediately
        self._http = HttpClient(
            self.base_url,
            self.api_key,
            self._request_timeout,
            self._poll_interval,
            self._poll_timeout
        )
        
        # Initialize registry
        logger.debug("Initializing service registry")
        self.registry = ServiceRegistry()
        self.registry.set_client(self)
        logger.info("BReactClient base initialization completed")
        
    @classmethod
    async def create(
        cls,
        base_url: str = "https://api-os.breact.ai",
        api_key: Optional[str] = None,
        request_timeout: int = 30,
        poll_interval: float = 1.0,
        poll_timeout: float = 180.0
    ) -> 'BReactClient':
        """Factory method to create and initialize a client instance"""
        logger.info("Creating new BReactClient instance...")
        client = cls(base_url, api_key, request_timeout, poll_interval, poll_timeout)
        logger.info("Initializing services...")
        await client._initialize_services()
        client._initialized = True
        logger.info("BReactClient initialization completed successfully")
        return client
        
    async def _initialize_services(self) -> None:
        """Fetch and initialize all available services"""
        if self._initialized:
            logger.debug("Services already initialized, skipping initialization")
            return
            
        logger.info("Fetching available services from API...")
        try:
            response = await self._http.request("GET", "/api/v1/services")
            logger.info(f"Found {len(response)} services")
            
            for service_data in response.values():
                service_id = service_data.get('id', 'unknown')
                logger.debug(f"Processing service: {service_id}")
                
                # Register service definition
                service = self.registry.register_service_definition(service_data)
                logger.debug(f"Registered service definition for {service.id}")
                
                # Create service instance
                if service.id in SERVICE_REGISTRY:
                    logger.debug(f"Using pre-built implementation for {service.id}")
                    # Use pre-built implementation
                    instance = self.registry.register_service_instance(SERVICE_REGISTRY[service.id])
                else:
                    logger.debug(f"Creating generic implementation for {service.id}")
                    # Create generic implementation
                    instance = self._create_generic_service(service)
                    
                logger.debug(f"Initializing service: {service.id}")
                await instance.initialize()
                # Store instance in both places for backward compatibility
                self._services[service.id] = instance
                self.registry._service_instances[service.id] = instance
                logger.debug(f"Service {service.id} initialized successfully")
                
        except Exception as e:
            logger.error(f"Error during service initialization: {str(e)}")
            raise

    async def _ensure_initialized(self) -> None:
        """Ensure client is initialized before operations"""
        if not self._initialized:
            logger.info("Client not initialized, performing initialization...")
            await self._initialize_services()
            self._initialized = True
            logger.info("Client initialization completed")

    async def analyze_targets(
        self,
        text: str,
        targets: List[str],
        additional_context: Optional[str] = None,
        model_id: str = "mistral-small",
        options: Optional[Dict[str, Any]] = None
    ) -> ServiceResponse:
        """Analyze targets in text using the target analyzer service"""
        logger.info("Analyzing targets...")
        await self._ensure_initialized()
        
        service = self._services.get("target_analyzer")
        if not service:
            logger.error("Target analyzer service not found")
            raise ServiceNotFoundError("Target analyzer service not found")
            
        logger.debug(f"Executing target analysis with model: {model_id}")
        params = {
            "text": text,
            "targets": targets,
            "model_id": model_id,
            "options": options or {}
        }
        if additional_context:
            params["additional_context"] = additional_context
            
        return await service.execute("analyze", params)

    async def ai_summarize(
        self,
        text: str,
        summary_type: str = "brief",
        model_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> ServiceResponse:
        """Summarize text using the AI summarization service"""
        logger.info("Summarizing text...")
        await self._ensure_initialized()
        
        service = self._services.get("aisummary")
        if not service:
            logger.error("AI Summarization service not found")
            raise ServiceNotFoundError("AI Summarization service not found")
            
        logger.debug(f"Executing AI summarization with type: {summary_type}")
        params = {
            "text": text,
            "summary_type": summary_type
        }
        
        if model_id:
            params["model_id"] = model_id
        if options:
            params["options"] = options
            
        return await service.execute("summarize", params)

    async def summarize(
        self,
        text: str,
        summary_type: str = "brief",
        model_id: Optional[str] = None,
        output_format: Optional[str] = None,
        max_words: Optional[int] = None,
        custom_requirements: Optional[List[str]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> ServiceResponse:
        """
        DEPRECATED: Use ai_summarize() instead.
        This method will be removed in a future version.
        """
        logger.warning("The summarize() method is deprecated. Please use ai_summarize() instead.")
        return await self.ai_summarize(
            text=text,
            summary_type=summary_type,
            model_id=model_id,
            options=options
        )

    async def generate_email_response(
        self,
        email_thread: List[Dict[str, str]],
        tone: str = "professional",
        style_guide: Optional[Dict[str, Any]] = None,
        key_points: Optional[List[str]] = None,
        model_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> ServiceResponse:
        """Generate an email response based on the email thread and parameters.
        
        Args:
            email_thread: List of previous email messages with sender, recipient, subject, content, timestamp
            tone: Desired tone (formal, casual, friendly, direct)
            style_guide: Dictionary containing language, max_length, signature, greeting_style
            key_points: List of specific points to address in the response
            model_id: Specific model to use for generation
            options: Additional model parameters
            
        Returns:
            ServiceResponse containing the generated email response
        """
        logger.info("Generating email response...")
        await self._ensure_initialized()
        
        service = self._services.get("email_response")
        if not service:
            logger.error("Email response service not found")
            raise ServiceNotFoundError("Email response service not found")
            
        logger.debug(f"Executing email response generation with tone: {tone}")
        params = {
            "email_thread": email_thread,
            "tone": tone
        }
        
        if style_guide:
            params["style_guide"] = style_guide
        if key_points:
            params["key_points"] = key_points
        if model_id:
            params["model_id"] = model_id
        if options:
            params["options"] = options
            
        return await service.execute("generate_response", params)

    async def analyze_email_thread(
        self,
        email_thread: List[Dict[str, str]],
        analysis_type: Optional[List[str]] = None,
        model_id: Optional[str] = None
    ) -> ServiceResponse:
        """Analyze an email thread for insights and suggestions.
        
        Args:
            email_thread: List of email messages to analyze
            analysis_type: List of analysis types (sentiment, key_points, action_items, response_urgency)
            model_id: Specific model to use for analysis
            
        Returns:
            ServiceResponse containing the analysis results
        """
        logger.info("Analyzing email thread...")
        await self._ensure_initialized()
        
        service = self._services.get("email_response")
        if not service:
            logger.error("Email response service not found")
            raise ServiceNotFoundError("Email response service not found")
            
        logger.debug("Executing email thread analysis")
        params = {
            "email_thread": email_thread
        }
        
        if analysis_type:
            params["analysis_type"] = analysis_type
        if model_id:
            params["model_id"] = model_id
            
        return await service.execute("analyze_thread", params)

    async def __aenter__(self) -> 'BReactClient':
        """Support async context manager"""
        logger.debug("Entering async context")
        await self._ensure_initialized()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Cleanup when used as context manager"""
        logger.debug("Exiting async context")
        await self.close()
        
    async def close(self):
        """Close the client and cleanup resources"""
        logger.info("Closing client and cleaning up resources...")
        if hasattr(self, '_http'):
            await self._http.close()
        self._initialized = False
        logger.info("Client closed successfully")

    def _create_generic_service(self, service_def: Service) -> BaseService:
        """Create a generic service implementation from a service definition"""
        logger.debug(f"Creating generic service for {service_def.id}")
        http_client = self._http  # Store reference to HTTP client
        
        class GenericService(BaseService):
            service_id = service_def.id
            service_config = service_def.config
            _service_definition = service_def
            
            def __init__(self, client: 'BReactClient'):
                super().__init__(client)
                self._http = http_client  # Use stored reference
            
            async def initialize(self) -> None:
                pass
                
            async def execute(self, endpoint: str, params: Dict[str, Any]) -> ServiceResponse:
                """Execute the service endpoint"""
                return await self._http.execute_with_polling(
                    method="POST",
                    path=f"/api/v1/services/{self.service_id}/{endpoint}",
                    json=params
                )
                
        return self.registry.register_service_instance(GenericService)

    async def execute_service(
        self,
        service_id: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> ServiceResponse:
        """Execute a service by ID."""
        if not self._initialized:
            raise BReactClientError("Client not initialized")

        # Get service instance (either pre-built or generic)
        service_instance = self.registry.get_service_instance(service_id)
        if not service_instance:
            raise ServiceNotFoundError(f"Service '{service_id}' not found")

        try:
            return await service_instance.execute(endpoint, params or {})
        except BReactError as e:
            logger.error(f"Error executing service {service_id}: {str(e)}")
            raise ServiceExecutionError(f"Error executing service {service_id}: {str(e)}")

    async def process_information(
        self,
        content: str,
        context: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        model_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> ServiceResponse:
        """
        Process information using the information tracker service.
        
        Args:
            content (str): The main content to process
            context (Optional[Dict[str, Any]]): Additional context information
            config (Optional[Dict[str, Any]]): Configuration including schema and model settings
            model_id (Optional[str]): ID of the model to use
            options (Optional[Dict[str, Any]]): Additional processing options
            
        Returns:
            ServiceResponse: The processed information result
        """
        await self._ensure_initialized()
        
        service = self._services.get("information_tracker")
        if not service:
            logger.error("Information tracker service not found")
            raise ServiceNotFoundError("Information tracker service not found")
            
        return await service.process_information(
            content=content,
            context=context,
            config=config,
            model_id=model_id,
            options=options
        )

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
        await self._ensure_initialized()
        
        service = self._services.get("information_tracker")
        if not service:
            logger.error("Information tracker service not found")
            raise ServiceNotFoundError("Information tracker service not found")
            
        return await service.extract_information(
            text=text,
            schema=schema,
            update_type=update_type,
            current_info=current_info,
            model_id=model_id
        )