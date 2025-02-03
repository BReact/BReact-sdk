from typing import Dict, Any
from datetime import datetime
from ..sdk.types.services import BaseService, ServiceConfig, Endpoint, ParameterDefinition, Service

class TargetAnalyzerService(BaseService):
    """Service for analyzing and updating targets based on conversation context"""
    service_id = "target_analyzer"
    
    # Define the service configuration with endpoints
    service_config = ServiceConfig(
        default_model="mistral-small"
    )
    
    async def initialize(self) -> None:
        """Initialize the target analyzer service."""
        self._service_definition = Service(
            id=self.service_id,
            name="Target Analyzer",
            description="Analyze and update targets based on conversation",
            version="1.0.0",
            author="BReact",
            path="/api/v1/services/target_analyzer",
            endpoints={
                "analyze_targets": Endpoint(
                    name="analyze_targets",
                    description="Analyze and update targets based on conversation",
                    method="POST",
                    parameters={
                        "text": ParameterDefinition(
                            type="string",
                            description="The conversation text to analyze",
                            required=True
                        ),
                        "targets": ParameterDefinition(
                            type="object",
                            description="Dictionary containing todo and done targets",
                            required=True
                        ),
                        "additional_context": ParameterDefinition(
                            type="string",
                            description="Additional context for analysis",
                            required=False
                        ),
                        "model_id": ParameterDefinition(
                            type="string",
                            description="ID of the model to use",
                            required=False,
                            default="mistral-small"
                        ),
                        "options": ParameterDefinition(
                            type="object",
                            description="Additional options for the analysis",
                            required=False
                        )
                    },
                    returns={"type": "object", "description": "Updated targets"}
                )
            },
            config=self.service_config,
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    async def analyze_targets(
        self,
        text: str,
        targets: Dict[str, Any],
        additional_context: str = "",
        model_id: str = "mistral-small",
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Analyze targets based on conversation text.
        
        Args:
            text: The conversation text to analyze
            targets: Dictionary containing todo and done targets
            additional_context: Additional context for analysis
            model_id: ID of the model to use
            options: Additional options for the analysis
            
        Returns:
            Dict containing updated targets
        """
        if options is None:
            options = {
                "tier": "standard",
                "format": "json",
                "temperature": 0,
                "max_tokens": 1000
            }
            
        params = {
            "text": text,
            "targets": targets,
            "additional_context": additional_context,
            "model_id": model_id,
            "options": options
        }
            
        return await self.execute("analyze_targets", params) 