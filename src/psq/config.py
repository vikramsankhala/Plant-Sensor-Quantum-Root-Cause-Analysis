"""
Configuration management for PSQ service.

Centralized configuration loading from environment variables,
with support for IBM Quantum credentials, backend selection,
and QUBO/QAOA hyperparameters.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class BackendConfig:
    """Configuration for quantum backend selection."""
    backend_type: str  # "simulator" or "ibm_quantum"
    backend_name: Optional[str] = None  # Specific backend name
    use_runtime: bool = False  # Use IBM Runtime vs direct backend access


@dataclass
class QaoaConfig:
    """Configuration for QAOA execution."""
    depth: int = 2  # Number of QAOA layers (p parameter)
    optimizer: str = "COBYLA"  # Optimizer name
    max_iterations: int = 100
    shots: int = 1024  # Number of measurement shots


@dataclass
class QuboConfig:
    """Configuration for QUBO hyperparameters."""
    alpha: float = 1.0  # Anomaly coverage weight
    beta: float = 1.0   # Pattern selection parsimony
    gamma: float = 1.0  # Pattern-sensor consistency


@dataclass
class ServiceConfig:
    """Main service configuration."""
    backend: BackendConfig
    qaoa: QaoaConfig
    qubo: QuboConfig
    ibm_quantum_token: Optional[str] = None
    ibm_quantum_instance: Optional[str] = None
    log_level: str = "INFO"
    timeout_seconds: int = 300


def load_config() -> ServiceConfig:
    """
    Load configuration from environment variables.
    
    Returns:
        ServiceConfig: Complete service configuration
    """
    backend_type = os.getenv("PSQ_BACKEND_TYPE", "simulator")
    backend_name = os.getenv("PSQ_BACKEND_NAME")
    
    backend_config = BackendConfig(
        backend_type=backend_type,
        backend_name=backend_name,
        use_runtime=os.getenv("PSQ_USE_RUNTIME", "false").lower() == "true",
    )
    
    qaoa_config = QaoaConfig(
        depth=int(os.getenv("PSQ_QAOA_DEPTH", "2")),
        optimizer=os.getenv("PSQ_QAOA_OPTIMIZER", "COBYLA"),
        max_iterations=int(os.getenv("PSQ_QAOA_MAX_ITER", "100")),
        shots=int(os.getenv("PSQ_QAOA_SHOTS", "1024")),
    )
    
    qubo_config = QuboConfig(
        alpha=float(os.getenv("PSQ_QUBO_ALPHA", "1.0")),
        beta=float(os.getenv("PSQ_QUBO_BETA", "1.0")),
        gamma=float(os.getenv("PSQ_QUBO_GAMMA", "1.0")),
    )
    
    return ServiceConfig(
        backend=backend_config,
        qaoa=qaoa_config,
        qubo=qubo_config,
        ibm_quantum_token=os.getenv("IBM_QUANTUM_TOKEN"),
        ibm_quantum_instance=os.getenv("IBM_QUANTUM_INSTANCE"),
        log_level=os.getenv("PSQ_LOG_LEVEL", "INFO"),
        timeout_seconds=int(os.getenv("PSQ_TIMEOUT_SECONDS", "300")),
    )

