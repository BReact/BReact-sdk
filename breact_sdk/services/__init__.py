from typing import Dict, Type
from ..sdk.types.services import BaseService
from .summarization import SummarizationService
from .target_analyzer import TargetAnalyzerService
from .information_tracker import InformationTrackerService
from .registry import ServiceRegistry

# Import other service implementations

# Registry of pre-built service implementations
SERVICE_REGISTRY: Dict[str, Type[BaseService]] = {
    "aisummary": SummarizationService,
    "target_analyzer": TargetAnalyzerService,
    "information_tracker": InformationTrackerService,
    # Add other services here
}

__all__ = [
    "ServiceRegistry",
    "SERVICE_REGISTRY",
    "SummarizationService",
    "TargetAnalyzerService",
    "InformationTrackerService",
]