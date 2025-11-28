<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Please extract the architecture from the attached file

The attached document defines a clear, layered architecture for a “quantum sidecar” service that performs plant sensor root‑cause analysis using QUBO + QAOA on IBM Quantum. Here is the extracted architecture.

***

## Service purpose and scope

- **Purpose:**
    - Accept plant sensor anomaly windows and a library of known root‑cause patterns.
    - Formulate a combinatorial optimization problem as a QUBO.
    - Convert QUBO → Ising Hamiltonian → Qiskit operator and solve with QAOA on IBM Quantum hardware or Aer simulators.
    - Return ranked root‑cause hypotheses with sensor coverage and diagnostics.[^1]
- **Scope:**
    - Focus only on combinatorial root‑cause assignment, not on initial anomaly detection.
    - Provide a clean HTTP API for integration with SAP AIN/PM/MES or edge agents.
    - Support both IBM Quantum backends and local simulators.[^1]

***

## High‑level data‑flow architecture

1. **Input acquisition**
    - Upstream system calls `POST /diagnose-plant-anomaly` with JSON:
        - Anomaly window ID and plant/context metadata.
        - List of abnormal sensors with severity scores.
        - Candidate root‑cause patterns and their sensor mappings, plus optional topology constraints.[^1]
2. **QUBO construction**
    - Build an energy function capturing:
        - Coverage of severe anomalies.
        - Sparsity (few patterns).
        - Consistency with known pattern–sensor links (from FMEA/topology).[^1]
3. **Quantum optimization**
    - Convert QUBO → Ising (spins) → Qiskit `SparsePauliOp` Hamiltonian.
    - Run QAOA via IBM Qiskit Runtime (hardware) or Aer (simulators) to approximately minimize the cost.[^1]
4. **Result post‑processing**
    - Decode bitstring samples into:
        - Ranked root‑cause sets with scores.
        - Which sensors each root cause explains, and residual anomalies.
        - Backend/quality metrics (energy, sample frequency, runtime, error info).[^1]

***

## Technology stack

- **Languages \& core tools**
    - Python 3.10+ as primary language.
    - Qiskit for QAOA, QUBO→Ising encoding, and IBM Runtime access.
    - (Optional) PennyLane for QML experiments.
    - FastAPI for the HTTP API/service layer.
    - pytest for unit/integration tests; mypy + ruff for static analysis and style.[^1]
- **Development environment**
    - Cursor IDE as AI‑assisted environment on top of VS Code, used for repo‑wide refactoring and “vibe coding”.
    - Optional Qiskit Code Assistant extension inside VS Code for quantum‑specific completions and templates.[^1]

***

## Package and repository structure

The document describes a `psq` package (plant sensor quantum) with clearly separated subpackages.[^1]

**Top‑level repo layout (conceptual):**

```text
plant-sensor-quantum/
  ARCHITECTURE.md
  README.md
  pyproject.toml / setup.cfg
  src/
    psq/
      __init__.py
      config.py
      logging_utils.py

      data/
        __init__.py
        schemas.py
        loaders.py
        featurization.py

      qubo/
        __init__.py
        model.py
        encode_ising.py
        postprocess.py

      quantum/
        __init__.py
        qiskit_runtime.py
        qaoa_solver.py
        simulators.py

      service/
        __init__.py
        api_models.py
        orchestrator.py

      api/
        __init__.py
        fastapi_app.py

  notebooks/
    01_qubo_playground.ipynb
    02_qaoa_tuning.ipynb
    03_ibm_runtime_integration.ipynb

  tests/
    test_qubo_model.py
    test_encode_ising.py
    test_qaoa_solver_sim.py
    test_service_endpoints.py
```


### Module responsibilities

- `psq/config.py`
    - Centralized configuration (env vars, IBM credentials, backend selection).[^1]
- `psq/logging_utils.py`
    - Structured logging configuration shared across modules.[^1]


#### `psq/data/`

- `schemas.py`
    - Pydantic models for:
        - `SensorAbnormal` (sensor ID, severity).
        - `RootCausePattern` (pattern ID, description, affected sensors, optional weights/topology).
        - `QuboRootCauseRequest` (anomaly ID, plant ID, sensor list, patterns, hyperparameters).
        - `QuboRootCauseResult` (solutions, backend metadata, diagnostics).[^1]
- `loaders.py`
    - Adapters to load anomaly windows, sensors, and patterns from SAP AIN/PM/MES or CSV/other sources.[^1]
- `featurization.py`
    - Optional feature engineering, severity scoring, window aggregation.[^1]


#### `psq/qubo/`

- `model.py`
    - Constructs QUBO for root‑cause diagnosis using binary variables for sensors and patterns and the specified energy formulation (coverage + sparsity + consistency).[^1]
- `encode_ising.py`
    - QUBO → Ising transform (binary {0,1} to spin {−1,+1}) and build of `SparsePauliOp` cost Hamiltonian.[^1]
- `postprocess.py`
    - Decode bitstring samples into root‑cause hypotheses, coverage metrics, and residual anomalies.[^1]


#### `psq/quantum/`

- `qiskit_runtime.py`
    - IBM Quantum Runtime session setup, Estimator/Sampler creation, backend selection, error handling.[^1]
- `qaoa_solver.py`
    - QAOA driver: build ansatz, connect cost operator, optimize parameters, and sample solutions on either simulators or IBM backends.[^1]
- `simulators.py`
    - Local Qiskit Aer simulators for dev/test; mocking of backends.[^1]


#### `psq/service/`

- `api_models.py`
    - Pydantic request/response models specifically for API layer, referencing `psq.data.schemas` where appropriate.[^1]
- `orchestrator.py`
    - High‑level orchestration:

```python
def diagnose_anomaly(
    request: QuboRootCauseRequest,
    qaoa_config: QaoaConfig,
) -> QuboRootCauseResult:
    # 1. Build QUBO
    # 2. Encode to Ising / SparsePauliOp
    # 3. Run QAOA
    # 4. Postprocess bitstrings into ranked root-cause hypotheses
```

    - This is the main callable for both API and other clients.[^1]


#### `psq/api/`

- `fastapi_app.py`
    - FastAPI application exposing:
        - `POST /diagnose-plant-anomaly` endpoint.
    - Handles HTTP concerns only; calls into `psq.service.orchestrator` for business logic.[^1]

***

## Development workflow and best practices

- **Architecture‑first:** maintain `ARCHITECTURE.md` as the single source of truth; update it before code changes.[^1]
- **Test‑driven:** prioritize tests for QUBO construction and post‑processing; use simulators and mocked backends for CI.[^1]
- **Notebook‑driven experiments:** explore QUBO variants and QAOA hyperparameters in `notebooks/` before integrating into `psq`.[^1]
- **Continuous architectural review:** keep code and `ARCHITECTURE.md` in sync; use Cursor for structure‑preserving refactors.[^1]

This is the core architecture extracted from the PDF; if you want, the next step can be to turn this into a concrete `ARCHITECTURE.md` text file, or to generate specific module skeletons (e.g., `psq/qubo/model.py` signatures) that you can paste into your repo.

<div align="center">⁂</div>

[^1]: Quantum-Sidecar-Architecture-for-Plant-Sensor-Root-Cause-Analysis.pdf

