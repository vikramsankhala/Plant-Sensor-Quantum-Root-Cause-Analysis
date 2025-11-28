"""
Pydantic request/response models for API layer.

These models reference psq.data.schemas where appropriate and provide
API-specific validation and serialization.
"""

from typing import Optional
from pydantic import BaseModel, Field
from psq.data.schemas import QuboRootCauseRequest, QuboRootCauseResult


class ErrorResponse(BaseModel):
    """Error response model for API."""
    
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    details: Optional[dict] = Field(None, description="Additional error details")


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    backend_available: bool = Field(..., description="Whether quantum backend is available")

