# Plant Sensor Quantum Root-Cause Analysis: Architecture Specification

## Service Purpose and Scope

### Purpose

This quantum sidecar service accepts plant sensor anomaly windows alongside a library of known root-cause patterns, formulates a combinatorial optimisation problem as a QUBO (Quadratic Unconstrained Binary Optimisation), solves it using QAOA (Quantum Approximate Optimisation Algorithm) on IBM Quantum hardware or simulators, and returns a ranked list of candidate root causes with their associated sensor coverage.

### Scope Definition

The service focuses exclusively on *combinatorial root-cause assignment*, not initial anomaly detection (which remains a classical preprocessing concern). It provides a clean HTTP API suitable for integration with SAP Asset Intelligence Network (AIN), Plant Maintenance (PM), Manufacturing Execution Systems (MES), or edge computing agents. The architecture supports both IBM Quantum backends and local Qiskit Aer simulators for development and testing workflows.

## High-Level Data Flow Architecture

### 1. Input Acquisition

Upstream systems (SAP AIN/PM/MES or dedicated anomaly detection services) invoke `POST /diagnose-plant-anomaly` with structured JSON payload containing:
- Anomaly window identifier and metadata
- List of abnormal sensors with severity scores (e.g., z-scores or residual magnitudes)
- Candidate root-cause patterns with their sensor mappings and optional topology constraints

### 2. QUBO Construction

The service constructs a QUBO energy function representing trade-offs between:
- Maximising coverage of severe anomalies
- Minimising the number of selected root-cause patterns (parsimony principle)
- Maintaining consistency with known pattern–sensor relationships derived from FMEA documentation and equipment topology graphs

### 3. Quantum Optimisation

The QUBO undergoes conversion to an Ising Hamiltonian, then transformation into a Qiskit `SparsePauliOp` suitable for quantum execution. QAOA runs via IBM Qiskit Runtime (for real quantum hardware) or local Aer simulators (for development), approximately minimising the cost function. Resulting bitstring samples encode candidate root-cause assignments.

### 4. Result Post-Processing

The service decodes bitstring samples into structured JSON responses containing:
- Ranked root-cause hypotheses with confidence scores
- Coverage metrics indicating which sensors each hypothesis explains
- Residual anomaly analysis for unexplained sensors
- Internal quality metrics (energy values, sample frequencies, backend execution metadata) for diagnostics and optimisation tuning

## Technology Stack

### Languages & Core Tools

- **Python 3.10+** as primary language
- **Qiskit** for QAOA, QUBO→Ising encoding, and IBM Runtime access
- **(Optional) PennyLane** for QML experiments
- **FastAPI** for the HTTP API/service layer
- **pytest** for unit/integration tests
- **mypy + ruff** for static analysis and style

### Development Environment

- **Cursor IDE** as AI-assisted environment on top of VS Code, used for repo-wide refactoring and "vibe coding"
- **(Optional) Qiskit Code Assistant** extension inside VS Code for quantum-specific completions and templates

## Repository Structure

```
plant-sensor-quantum/
├── ARCHITECTURE.md          # This document
├── README.md                # Quick start and overview
├── pyproject.toml           # Dependencies and build config
├── src/
│   └── psq/                 # Main package
│       ├── __init__.py
│       ├── config.py        # Configuration management
│       ├── logging_utils.py # Structured logging
│       ├── data/            # Data models and ingestion
│       │   ├── __init__.py
│       │   ├── schemas.py   # Pydantic models
│       │   ├── loaders.py   # SAP/CSV adapters
│       │   └── featurization.py
│       ├── qubo/            # QUBO formulation
│       │   ├── __init__.py
│       │   ├── model.py     # QUBO construction
│       │   ├── encode_ising.py
│       │   └── postprocess.py
│       ├── quantum/         # Quantum execution
│       │   ├── __init__.py
│       │   ├── qiskit_runtime.py
│       │   ├── qaoa_solver.py
│       │   └── simulators.py
│       ├── service/         # Business logic
│       │   ├── __init__.py
│       │   ├── api_models.py
│       │   └── orchestrator.py
│       └── api/             # HTTP interface
│           ├── __init__.py
│           └── fastapi_app.py
├── notebooks/               # Jupyter exploration
│   ├── 01_qubo_playground.ipynb
│   ├── 02_qaoa_tuning.ipynb
│   └── 03_ibm_runtime_integration.ipynb
└── tests/                   # Comprehensive test suite
    ├── test_qubo_model.py
    ├── test_encode_ising.py
    ├── test_qaoa_solver_sim.py
    └── test_service_endpoints.py
```

This modular structure enforces clear separation of concerns: data handling remains isolated from quantum logic, which stays independent of API exposure. Each package addresses a single architectural responsibility, facilitating parallel development and straightforward testing.

## Module Responsibilities

### Core Configuration

#### `psq/config.py`
Centralized configuration management:
- Environment variable loading
- IBM Quantum credentials management
- Backend selection (simulator vs hardware)
- QUBO hyperparameter defaults
- QAOA configuration (depth, optimizer settings)

#### `psq/logging_utils.py`
Structured logging configuration shared across modules:
- JSON-formatted log output
- Contextual logging with request IDs
- Log level configuration
- Integration with log aggregation systems

### Data Layer (`psq/data/`)

#### `schemas.py`
Pydantic data models for type-safe data structures:
- `SensorAbnormal`: Represents a single anomalous sensor reading
  - `sensor_id: str` - Physical sensor identifier
  - `severity: float` - Abnormality magnitude (z-score, residual, or domain-specific metric)
- `RootCausePattern`: Encodes known failure modes
  - `pattern_id: str` - Unique pattern identifier
  - `description: str` - Human-readable description
  - `affected_sensors: List[str]` - Sensor coverage
  - Optional fields for weights or topology tags
- `QuboRootCauseRequest`: Complete input payload
  - `anomaly_id: str` - Anomaly window identifier
  - `plant_id: str` - Plant identifier for traceability
  - `abnormal_sensors: List[SensorAbnormal]` - List of abnormal sensors
  - `patterns: List[RootCausePattern]` - Pattern library
  - Optional QUBO hyperparameters (alpha, beta, gamma)
- `QuboRootCauseResult`: Structured output
  - `anomaly_id: str` - Echoed from request
  - `solutions: List[Solution]` - Ranked root-cause hypotheses
  - `backend_metadata: BackendMetadata` - Execution information
  - `quality_metrics: QualityMetrics` - Diagnostic quality indicators

#### `loaders.py`
Adapters to load anomaly windows, sensors, and patterns:
- SAP AIN/PM/MES integration via OData APIs
- CSV file loaders for development/testing
- Pattern library management
- Data validation and transformation

#### `featurization.py`
Optional feature engineering:
- Severity scoring (z-score computation, residual calculation)
- Window aggregation
- Sensor correlation analysis
- Temporal feature extraction

### QUBO Layer (`psq/qubo/`)

#### `model.py`
Constructs QUBO for root-cause diagnosis.

**Energy Function Formulation:**
```
E(z, y) = α·Σᵢ wᵢ(1 - zᵢ) + β·Σⱼ yⱼ + γ·Σᵢ(Σⱼ zᵢ - Aᵢⱼyⱼ)²
```

Where:
- **First term**: Penalty for dismissing severe anomalies (wᵢ encodes severity)
- **Second term**: Pattern selection cost promoting parsimonious explanations
- **Third term**: Consistency enforcement (Aᵢⱼ indicates whether pattern j affects sensor i)

**Binary Variables:**
- **zᵢ (sensor variables)**: Binary indicator for sensor i being genuinely anomalous
- **yⱼ (pattern variables)**: Binary indicator for root-cause pattern j being active

**Function Signature:**
```python
def build_root_cause_qubo(
    sensors: List[SensorAbnormal],
    patterns: List[RootCausePattern],
    alpha: float,
    beta: float,
    gamma: float,
) -> Tuple[Dict[Tuple[str, str], float], Dict[str, int]]:
    """
    Construct QUBO for root-cause diagnosis.
    
    Returns:
        qubo_dict: Mapping from variable pairs to coefficients
        var_index: Mapping from variable names to qubit indices
    """
```

#### `encode_ising.py`
QUBO → Ising transformation:
- Convert binary {0,1} variables to spin {-1,+1} variables
- Build Ising coefficients (hᵢ local fields, Jᵢⱼ couplings)
- Construct Qiskit `SparsePauliOp` cost Hamiltonian
- Handle constant energy offset

**Function Signature:**
```python
def qubo_to_ising_hamiltonian(
    qubo_dict: Dict[Tuple[str, str], float],
    var_index: Dict[str, int],
) -> SparsePauliOp:
    """
    Convert QUBO dictionary to Ising Hamiltonian (SparsePauliOp).
    """
```

#### `postprocess.py`
Decode bitstring samples into root-cause hypotheses:
- Extract sensor and pattern assignments from bitstrings
- Rank solutions by energy and sample frequency
- Compute coverage metrics
- Identify residual unexplained anomalies
- Calculate confidence scores

### Quantum Layer (`psq/quantum/`)

#### `qiskit_runtime.py`
IBM Quantum Runtime session management:
- Runtime session setup and teardown
- Estimator/Sampler creation
- Backend selection and validation
- Error handling and retry logic
- Circuit breaker pattern implementation

#### `qaoa_solver.py`
QAOA driver implementation:
- Build parameterised QAOA ansatz
- Connect cost operator (SparsePauliOp)
- Optimize variational parameters
- Sample solutions on simulators or IBM backends
- Return bitstring distributions with metadata

**Function Signature:**
```python
def run_qaoa_root_cause(
    cost_operator: SparsePauliOp,
    backend_config: BackendConfig,
    qaoa_depth: int,
    optimizer: Optional[Optimizer] = None,
) -> QAOAResult:
    """
    Execute QAOA for root-cause diagnosis.
    
    Returns:
        Optimized parameters, minimum energy, bitstring samples
    """
```

#### `simulators.py`
Local Qiskit Aer simulators:
- Simulator backend creation
- Mock backend implementations for testing
- Simulator-specific optimizations
- Statevector and shot-based simulation modes

### Service Layer (`psq/service/`)

#### `api_models.py`
Pydantic request/response models for API layer:
- Request validation models
- Response serialization models
- Error response models
- References `psq.data.schemas` where appropriate

#### `orchestrator.py`
High-level orchestration function:

**Function Signature:**
```python
def diagnose_anomaly(
    request: QuboRootCauseRequest,
    qaoa_config: QaoaConfig,
) -> QuboRootCauseResult:
    """
    Main orchestration function for root-cause diagnosis.
    
    Workflow:
    1. Build QUBO from sensors and patterns
    2. Encode QUBO as Ising Hamiltonian (SparsePauliOp)
    3. Execute QAOA with specified backend and depth
    4. Decode bitstrings into ranked root-cause hypotheses
    5. Compute coverage metrics and quality scores
    6. Package results with metadata
    
    Handles backend failures gracefully with fallback strategies.
    """
```

### API Layer (`psq/api/`)

#### `fastapi_app.py`
FastAPI application:
- `POST /diagnose-plant-anomaly` endpoint
- Request validation via Pydantic
- Response serialization
- Error handling (400, 503 status codes)
- Structured logging integration
- OpenAPI/Swagger documentation

**Architectural Constraint**: HTTP concerns belong exclusively in this module. All business logic delegates to `psq.service.orchestrator`.

## Development Workflow and Best Practices

### Architecture-First Design

Maintain `ARCHITECTURE.md` as the single source of truth. Update it before code changes. Use this document as a contract between team members and reference for AI-assisted implementation.

### Test-Driven Development

Prioritize tests for QUBO construction and post-processing logic. Use simulators and mocked backends for CI/CD pipelines. Test categories:
- **Unit tests**: Pure QUBO logic, Ising encoding, post-processing
- **Integration tests**: End-to-end API flows with simulator backends
- **Quantum simulator tests**: Validate QAOA behavior on small instances

### Notebook-Driven Experimentation

Explore QUBO variants and QAOA hyperparameters in Jupyter notebooks before integrating into production code. Notebooks serve as:
- Rapid prototyping environment
- Executable documentation
- Validation test cases

### Continuous Architectural Review

Regularly assess codebase alignment with `ARCHITECTURE.md`. As implementation proceeds, update documentation promptly and use Cursor to propagate changes. Never allow documentation and code to drift.

## Key Architectural Principles

### Separation of Concerns

Maintain strict boundaries between:
- Data models (`psq/data/`)
- QUBO formulation (`psq/qubo/`)
- Quantum execution (`psq/quantum/`)
- Business logic (`psq/service/`)
- API exposure (`psq/api/`)

Never let quantum-specific concerns leak into business logic or API layers.

### Configuration Over Code

Externalize all environment-specific settings:
- Backend selection
- QUBO hyperparameters
- Timeout thresholds
- Logging verbosity

Configuration-driven behavior enables operational teams to tune system behavior without developer involvement.

### Observability by Default

Instrument every component with:
- Comprehensive structured logging
- Metric emission
- Distributed tracing

Log everything: inputs, intermediate results, quantum execution metadata, and outputs.

### Graceful Degradation

Design for resilience against quantum backend unavailability:
- Intelligent fallbacks to simulators
- Cached results where appropriate
- Circuit breaker patterns
- Never allow quantum infrastructure issues to cause complete service failures

## Testing Strategy

### Unit Tests

- **test_qubo_model.py**: Verify QUBO construction logic using toy problem instances with known optimal solutions
- **test_encode_ising.py**: Confirm QUBO-to-Ising transformation preserves optimization landscape

### Quantum Simulator Tests

- **test_qaoa_solver_sim.py**: Execute QAOA on Qiskit Aer simulator for small QUBO instances where brute-force optimal solutions are tractable

### Integration Tests

- **test_service_endpoints.py**: Exercise complete end-to-end flow using FastAPI TestClient. Submit synthetic anomaly scenarios, verify response structure and content correctness

## Environment Configuration

### Development
- Simulator-only execution
- No IBM Quantum credentials required
- Fast feedback loops

### Staging
- IBM Runtime with restricted qubit counts and shot budgets
- Cost control measures
- Smoke tests on critical paths

### Production
- Full IBM Runtime access with fallback strategies
- Feature flags for gradual rollout
- Comprehensive benchmarking and alerting infrastructure

## Performance Targets

- **API Latency**: <100ms for simulator-based diagnosis (excluding quantum hardware queue time)
- **IBM Runtime Response**: 2-5s typical quantum hardware execution (varies with backend load)
- **Service Availability**: 99.5% target (accounting for quantum backend unavailability)

## Security Considerations

- **API Authentication**: OAuth2 or API key-based authentication
- **Data Protection**: Encrypt sensitive sensor data at rest and in transit (TLS 1.3)
- **IBM Quantum Credentials**: Store securely using secret management systems (Vault, AWS Secrets Manager, Azure Key Vault)
- **Log Sanitization**: Prevent inadvertent exposure of proprietary pattern libraries

## Future Extensions

### Topology-Aware Constraints
Enhance QUBO formulation with equipment topology awareness for physically adjacent equipment correlation.

### Temporal Pattern Sequences
Extend QUBO to model temporal causality for anomaly windows spanning multiple time steps.

### Quantum Machine Learning
Explore PennyLane integration for pattern discovery and anomaly prediction using variational quantum classifiers.

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Maintainer**: Architecture Team

