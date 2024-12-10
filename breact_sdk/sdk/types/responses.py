from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, field_validator
from datetime import datetime

class ProcessInfo(BaseModel):
    service: str
    endpoint: str
    created_at: datetime

class ServiceResult(BaseModel):
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ServiceResponse(BaseModel):
    """Response from a service execution."""
    status: str
    result: Optional[ServiceResult] = None
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