"""
Pydantic data models for type-safe data structures.

These models serve as contracts between service layers and external systems,
providing automatic validation, serialization, and OpenAPI schema generation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class SensorAbnormal(BaseModel):
    """Represents a single anomalous sensor reading."""
    
    sensor_id: str = Field(..., description="Physical sensor identifier")
    severity: float = Field(..., description="Abnormality magnitude (z-score, residual, or domain-specific metric)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sensor_id": "TEMP_001",
                "severity": 2.5,
            }
        }


class RootCausePattern(BaseModel):
    """Encodes known failure modes with sensor coverage."""
    
    pattern_id: str = Field(..., description="Unique pattern identifier")
    description: str = Field(..., description="Human-readable description")
    affected_sensors: List[str] = Field(..., description="List of sensor IDs affected by this pattern")
    weight: Optional[float] = Field(None, description="Optional pattern weight")
    topology_tags: Optional[List[str]] = Field(None, description="Optional topology constraint tags")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pattern_id": "PUMP_CAVITATION",
                "description": "Pump cavitation causing pressure fluctuations",
                "affected_sensors": ["PRESSURE_001", "FLOW_001"],
                "weight": 1.0,
            }
        }


class QuboRootCauseRequest(BaseModel):
    """Complete input payload for root-cause diagnosis."""
    
    anomaly_id: str = Field(..., description="Anomaly window identifier")
    plant_id: str = Field(..., description="Plant identifier for traceability")
    abnormal_sensors: List[SensorAbnormal] = Field(..., description="List of abnormal sensors")
    patterns: List[RootCausePattern] = Field(..., description="Library of candidate root-cause patterns")
    alpha: Optional[float] = Field(None, description="QUBO hyperparameter: anomaly coverage weight")
    beta: Optional[float] = Field(None, description="QUBO hyperparameter: pattern selection parsimony")
    gamma: Optional[float] = Field(None, description="QUBO hyperparameter: pattern-sensor consistency")
    
    class Config:
        json_schema_extra = {
            "example": {
                "anomaly_id": "ANOM_2024_001",
                "plant_id": "PLANT_A",
                "abnormal_sensors": [
                    {"sensor_id": "TEMP_001", "severity": 2.5},
                    {"sensor_id": "PRESSURE_001", "severity": 3.0},
                ],
                "patterns": [
                    {
                        "pattern_id": "PUMP_CAVITATION",
                        "description": "Pump cavitation",
                        "affected_sensors": ["PRESSURE_001", "FLOW_001"],
                    }
                ],
            }
        }


class Solution(BaseModel):
    """A single root-cause hypothesis solution."""
    
    selected_patterns: List[str] = Field(..., description="List of selected pattern IDs")
    covered_sensors: List[str] = Field(..., description="List of sensor IDs explained by this solution")
    confidence_score: float = Field(..., description="Confidence score (0-100)")
    energy: float = Field(..., description="QUBO energy value")
    sample_frequency: float = Field(..., description="Frequency of this solution in QAOA samples")


class BackendMetadata(BaseModel):
    """Metadata about quantum backend execution."""
    
    backend_name: str = Field(..., description="Backend identifier")
    backend_type: str = Field(..., description="Backend type (simulator/hardware)")
    execution_time_seconds: float = Field(..., description="Execution time in seconds")
    shots: int = Field(..., description="Number of measurement shots")
    qaoa_depth: int = Field(..., description="QAOA depth parameter")


class QualityMetrics(BaseModel):
    """Quality metrics for diagnostic results."""
    
    coverage_rate: float = Field(..., description="Percentage of sensors explained")
    average_pattern_count: float = Field(..., description="Average number of patterns per solution")
    residual_anomalies: List[str] = Field(..., description="List of unexplained sensor IDs")


class QuboRootCauseResult(BaseModel):
    """Structured output from root-cause diagnosis."""
    
    anomaly_id: str = Field(..., description="Echoed from request")
    solutions: List[Solution] = Field(..., description="Ranked list of root-cause hypotheses")
    backend_metadata: BackendMetadata = Field(..., description="Backend execution information")
    quality_metrics: QualityMetrics = Field(..., description="Diagnostic quality indicators")

