# Plant Sensor Quantum Root-Cause Analysis

## What is This Project?

This project is a **quantum computing service** that helps industrial plants (like factories, power plants, or manufacturing facilities) quickly identify the root causes of equipment problems by analyzing sensor data.

### The Problem It Solves

In industrial plants, hundreds or thousands of sensors constantly monitor equipment—measuring temperature, pressure, flow rates, vibration, and more. When something goes wrong, multiple sensors often show abnormal readings simultaneously. The challenge is:

- **Which sensor readings are the real problem?** (vs. false alarms)
- **What's the actual root cause?** (a single failure can trigger multiple sensor alerts)
- **Which sensors are related?** (some failures affect multiple sensors together)

Traditional methods can be slow and miss complex relationships between sensors. This service uses **quantum computing** to analyze all possibilities simultaneously and find the most likely root cause faster.

### How It Works (In Simple Terms)

1. **You provide input**: A list of sensors showing abnormal readings and a library of known failure patterns (like "pump cavitation affects pressure and flow sensors")

2. **The system creates an optimization problem**: It converts your sensor data into a mathematical problem that asks: "What combination of known failure patterns best explains all the abnormal sensors?"

3. **Quantum computing solves it**: Using IBM's quantum computers (or simulators for testing), the system explores many possible explanations at once and finds the best answer

4. **You get ranked results**: The service returns a list of likely root causes, ranked by confidence, showing which sensors each root cause explains

### Who Is This For?

- **Plant maintenance engineers** who need to quickly diagnose equipment failures
- **Industrial operations teams** integrating with SAP or other enterprise systems
- **Data scientists and engineers** working on predictive maintenance
- **Researchers** exploring quantum computing applications in industrial settings

### What You Need to Know

**To use this service**, you need:
- Basic understanding of REST APIs (or willingness to learn)
- Access to sensor data from your plant
- A library of known failure patterns (or willingness to build one)

**To develop or modify this service**, you should understand:
- Python programming
- Quantum computing basics (QUBO, QAOA)
- FastAPI web frameworks
- Industrial sensor systems

### Key Concepts Explained Simply

- **QUBO (Quadratic Unconstrained Binary Optimization)**: A mathematical way to represent the problem of finding the best explanation for sensor anomalies
- **QAOA (Quantum Approximate Optimization Algorithm)**: A quantum computing algorithm that solves optimization problems like finding root causes
- **Sidecar Service**: A separate service that works alongside your main plant systems (like SAP) to provide specialized analysis
- **Simulator vs. Hardware**: You can test with free quantum simulators (fast, no cost) or run on real IBM quantum computers (slower, costs money, but potentially more powerful)

### Real-World Example

Imagine a chemical plant where:
- Temperature sensor shows high readings
- Pressure sensor shows low readings  
- Flow sensor shows erratic readings

The system might identify that "pump cavitation" (a known failure pattern) explains all three sensors, rather than three separate problems. This helps maintenance teams fix the actual root cause instead of chasing multiple symptoms.

---

## Technical Overview

A quantum sidecar service for industrial plant sensor anomaly diagnosis using QUBO formulation and QAOA optimization on IBM Quantum hardware.

This service accepts plant sensor anomaly windows alongside a library of known root-cause patterns, formulates a combinatorial optimization problem as a QUBO, solves it using QAOA on IBM Quantum hardware or simulators, and returns ranked root-cause hypotheses with sensor coverage.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for comprehensive architectural documentation.

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd plant-sensor-quantum
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e ".[dev]"
```

### Configuration

Set environment variables for configuration:

```bash
# Backend selection
export PSQ_BACKEND_TYPE=simulator  # or "ibm_quantum"
export PSQ_BACKEND_NAME=aer_simulator

# QAOA configuration
export PSQ_QAOA_DEPTH=2
export PSQ_QAOA_SHOTS=1024

# QUBO hyperparameters
export PSQ_QUBO_ALPHA=1.0
export PSQ_QUBO_BETA=1.0
export PSQ_QUBO_GAMMA=1.0

# IBM Quantum (if using hardware)
export IBM_QUANTUM_TOKEN=your_token_here
export IBM_QUANTUM_INSTANCE=your_instance_here
```

### Running the Service

Start the FastAPI service:

```bash
uvicorn psq.api.fastapi_app:app --reload
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

### Example Request

```bash
curl -X POST "http://localhost:8000/diagnose-plant-anomaly" \
  -H "Content-Type: application/json" \
  -d '{
    "anomaly_id": "ANOM_2024_001",
    "plant_id": "PLANT_A",
    "abnormal_sensors": [
      {"sensor_id": "TEMP_001", "severity": 2.5},
      {"sensor_id": "PRESSURE_001", "severity": 3.0}
    ],
    "patterns": [
      {
        "pattern_id": "PUMP_CAVITATION",
        "description": "Pump cavitation causing pressure fluctuations",
        "affected_sensors": ["PRESSURE_001", "FLOW_001"]
      }
    ]
  }'
```

## Development

### Project Structure

```
plant-sensor-quantum/
├── ARCHITECTURE.md          # Architecture documentation
├── README.md                # This file
├── pyproject.toml           # Dependencies and build config
├── src/
│   └── psq/                 # Main package
│       ├── config.py        # Configuration management
│       ├── logging_utils.py # Structured logging
│       ├── data/            # Data models and ingestion
│       ├── qubo/            # QUBO formulation
│       ├── quantum/         # Quantum execution
│       ├── service/         # Business logic
│       └── api/             # HTTP interface
├── notebooks/               # Jupyter exploration
└── tests/                   # Test suite
```

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

Format code:
```bash
black src/ tests/
ruff check src/ tests/
```

Type checking:
```bash
mypy src/
```

### Jupyter Notebooks

Explore QUBO formulations and QAOA tuning in the `notebooks/` directory:

```bash
jupyter notebook notebooks/
```

## Key Features

- **QUBO Formulation**: Converts sensor anomalies and root-cause patterns into combinatorial optimization problems
- **QAOA Execution**: Solves QUBO using Quantum Approximate Optimization Algorithm on IBM Quantum hardware or simulators
- **RESTful API**: Clean HTTP interface for integration with SAP systems and edge agents
- **Structured Logging**: JSON-formatted logs for integration with log aggregation systems
- **Graceful Degradation**: Automatic fallback to simulators when quantum hardware is unavailable

## Technology Stack

- **Python 3.10+**: Primary language
- **Qiskit**: Quantum SDK for QAOA and IBM Quantum integration
- **FastAPI**: Modern web framework for API layer
- **Pydantic**: Type-safe data validation
- **pytest**: Testing framework

## Contributing

1. Review [ARCHITECTURE.md](ARCHITECTURE.md) to understand system design
2. Follow architecture-first development: update architecture docs before code changes
3. Write tests for new functionality
4. Ensure code passes linting and type checking

## License

MIT License

## References

- [Qiskit Documentation](https://qiskit.org/documentation/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ARCHITECTURE.md](ARCHITECTURE.md) - Complete architectural specification

