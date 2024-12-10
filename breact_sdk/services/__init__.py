from typing import Dict, Type
from ..sdk.types.services import BaseService
from .summarization import SummarizationService
from .registry import ServiceRegistry

# Import other service implementations

# Registry of pre-built service implementations
SERVICE_REGISTRY: Dict[str, Type[BaseService]] = {
    "summarizer": SummarizationService,
    # Add other services here
}

__all__ = ["ServiceRegistry", "SERVICE_REGISTRY"]