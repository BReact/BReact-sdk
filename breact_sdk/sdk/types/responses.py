from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, field_validator
from datetime import datetime

class ProcessInfo(BaseModel):
    service: str
    endpoint: str
    created_at: datetime

class ServiceResult(BaseModel):
    status: str
    result: Optional[Union[Dict[str, Any], Any]] = None  # Can be any JSON structure
    error: Optional[str] = None

    # Allow creation from dict without requiring all fields
    model_config = {
        "extra": "allow"
    }

class ServiceResponse(BaseModel):
    """Response from a service execution."""
    status: str  # completed, pending, error
    result: Optional[Union[ServiceResult, Dict[str, Any]]] = None  # Can be either a ServiceResult or raw dict
    error: Optional[str] = None
    message: Optional[str] = None
    service: Optional[str] = None
    endpoint: Optional[str] = None
    created_at: Optional[datetime] = None
    process_info: Optional[ProcessInfo] = None

class ProcessResponse(BaseModel):
    process_id: Union[str, int]
    access_token: str
    
    @field_validator('process_id')
    @classmethod
    def convert_process_id_to_str(cls, v: Union[str, int]) -> str:
        """Convert process_id to string regardless of input type"""
        return str(v)