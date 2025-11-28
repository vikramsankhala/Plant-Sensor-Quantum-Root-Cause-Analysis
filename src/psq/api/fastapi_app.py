"""
FastAPI application for plant sensor root-cause diagnosis service.

Exposes HTTP endpoints for anomaly diagnosis with proper validation,
error handling, and OpenAPI documentation.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from psq.config import load_config
from psq.data.schemas import QuboRootCauseRequest, QuboRootCauseResult
from psq.logging_utils import get_logger, setup_logging
from psq.service.orchestrator import diagnose_anomaly

# Initialize logging
config = load_config()
setup_logging(config.log_level)
logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Plant Sensor Quantum Root-Cause Analysis",
    description="Quantum sidecar service for industrial plant sensor anomaly diagnosis",
    version="0.1.0",
)

# Project description HTML content
PROJECT_DESCRIPTION_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plant Sensor Quantum Root-Cause Analysis</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }
        .header p {
            font-size: 1.2em;
            opacity: 0.95;
        }
        .content {
            padding: 40px;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }
        .section h3 {
            color: #764ba2;
            font-size: 1.4em;
            margin-top: 25px;
            margin-bottom: 12px;
        }
        .section p {
            margin-bottom: 15px;
            font-size: 1.05em;
        }
        .section ul {
            margin-left: 30px;
            margin-bottom: 15px;
        }
        .section li {
            margin-bottom: 8px;
            font-size: 1.05em;
        }
        .highlight-box {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .example-box {
            background: #e8f4f8;
            border-left: 4px solid #17a2b8;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .concept-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .concept-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-top: 4px solid #667eea;
        }
        .concept-card strong {
            color: #667eea;
            display: block;
            margin-bottom: 8px;
            font-size: 1.1em;
        }
        .nav-links {
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            border-top: 2px solid #e9ecef;
        }
        .nav-links a {
            display: inline-block;
            margin: 0 15px;
            padding: 12px 30px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            transition: background 0.3s;
        }
        .nav-links a:hover {
            background: #764ba2;
        }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            background: #667eea;
            color: white;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌿 Plant Sensor Quantum Root-Cause Analysis</h1>
            <p>Quantum-Powered Industrial Diagnostics Service</p>
            <span class="badge">Version 0.1.0</span>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>What is This Project?</h2>
                <p>This project is a <strong>quantum computing service</strong> that helps industrial plants (like factories, power plants, or manufacturing facilities) quickly identify the root causes of equipment problems by analyzing sensor data.</p>
            </div>

            <div class="section">
                <h2>The Problem It Solves</h2>
                <p>In industrial plants, hundreds or thousands of sensors constantly monitor equipment—measuring temperature, pressure, flow rates, vibration, and more. When something goes wrong, multiple sensors often show abnormal readings simultaneously. The challenge is:</p>
                <ul>
                    <li><strong>Which sensor readings are the real problem?</strong> (vs. false alarms)</li>
                    <li><strong>What's the actual root cause?</strong> (a single failure can trigger multiple sensor alerts)</li>
                    <li><strong>Which sensors are related?</strong> (some failures affect multiple sensors together)</li>
                </ul>
                <p>Traditional methods can be slow and miss complex relationships between sensors. This service uses <strong>quantum computing</strong> to analyze all possibilities simultaneously and find the most likely root cause faster.</p>
            </div>

            <div class="section">
                <h2>How It Works (In Simple Terms)</h2>
                <div class="highlight-box">
                    <ol style="margin-left: 20px;">
                        <li><strong>You provide input:</strong> A list of sensors showing abnormal readings and a library of known failure patterns (like "pump cavitation affects pressure and flow sensors")</li>
                        <li><strong>The system creates an optimization problem:</strong> It converts your sensor data into a mathematical problem that asks: "What combination of known failure patterns best explains all the abnormal sensors?"</li>
                        <li><strong>Quantum computing solves it:</strong> Using IBM's quantum computers (or simulators for testing), the system explores many possible explanations at once and finds the best answer</li>
                        <li><strong>You get ranked results:</strong> The service returns a list of likely root causes, ranked by confidence, showing which sensors each root cause explains</li>
                    </ol>
                </div>
            </div>

            <div class="section">
                <h2>Who Is This For?</h2>
                <ul>
                    <li><strong>Plant maintenance engineers</strong> who need to quickly diagnose equipment failures</li>
                    <li><strong>Industrial operations teams</strong> integrating with SAP or other enterprise systems</li>
                    <li><strong>Data scientists and engineers</strong> working on predictive maintenance</li>
                    <li><strong>Researchers</strong> exploring quantum computing applications in industrial settings</li>
                </ul>
            </div>

            <div class="section">
                <h2>What You Need to Know</h2>
                <h3>To use this service:</h3>
                <ul>
                    <li>Basic understanding of REST APIs (or willingness to learn)</li>
                    <li>Access to sensor data from your plant</li>
                    <li>A library of known failure patterns (or willingness to build one)</li>
                </ul>
                <h3>To develop or modify this service:</h3>
                <ul>
                    <li>Python programming</li>
                    <li>Quantum computing basics (QUBO, QAOA)</li>
                    <li>FastAPI web frameworks</li>
                    <li>Industrial sensor systems</li>
                </ul>
            </div>

            <div class="section">
                <h2>Key Concepts Explained Simply</h2>
                <div class="concept-grid">
                    <div class="concept-card">
                        <strong>QUBO</strong>
                        <p>A mathematical way to represent the problem of finding the best explanation for sensor anomalies</p>
                    </div>
                    <div class="concept-card">
                        <strong>QAOA</strong>
                        <p>A quantum computing algorithm that solves optimization problems like finding root causes</p>
                    </div>
                    <div class="concept-card">
                        <strong>Sidecar Service</strong>
                        <p>A separate service that works alongside your main plant systems (like SAP) to provide specialized analysis</p>
                    </div>
                    <div class="concept-card">
                        <strong>Simulator vs. Hardware</strong>
                        <p>You can test with free quantum simulators (fast, no cost) or run on real IBM quantum computers (slower, costs money, but potentially more powerful)</p>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>Real-World Example</h2>
                <div class="example-box">
                    <p>Imagine a chemical plant where:</p>
                    <ul>
                        <li>Temperature sensor shows high readings</li>
                        <li>Pressure sensor shows low readings</li>
                        <li>Flow sensor shows erratic readings</li>
                    </ul>
                    <p><strong>The system might identify that "pump cavitation"</strong> (a known failure pattern) explains all three sensors, rather than three separate problems. This helps maintenance teams fix the actual root cause instead of chasing multiple symptoms.</p>
                </div>
            </div>

            <div class="section">
                <h2>Technical Architecture</h2>
                <p>The system follows a <strong>layered architecture</strong> with clear separation of concerns, enabling independent development, testing, and maintenance of each component.</p>
                
                <h3>🏗️ System Layers</h3>
                <div class="highlight-box">
                    <ol style="margin-left: 20px;">
                        <li><strong>API Layer</strong> (FastAPI) - Handles HTTP requests, validation, and responses</li>
                        <li><strong>Service Layer</strong> - Orchestrates the diagnosis workflow</li>
                        <li><strong>QUBO Layer</strong> - Converts sensor data into optimization problems</li>
                        <li><strong>Quantum Layer</strong> - Executes QAOA on quantum hardware or simulators</li>
                        <li><strong>Data Layer</strong> - Manages data models and ingestion</li>
                    </ol>
                </div>

                <h3>🔄 Data Flow</h3>
                <div class="example-box">
                    <p><strong>Step 1: Input Acquisition</strong><br>
                    Upstream systems (SAP, MES, or anomaly detection services) send JSON payloads with abnormal sensors and known failure patterns.</p>
                    
                    <p><strong>Step 2: QUBO Construction</strong><br>
                    The system builds a mathematical optimization problem (QUBO) that balances:
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li>Coverage of severe anomalies</li>
                        <li>Minimizing the number of selected patterns (parsimony)</li>
                        <li>Consistency with known pattern-sensor relationships</li>
                    </ul>
                    </p>
                    
                    <p><strong>Step 3: Quantum Optimization</strong><br>
                    The QUBO is converted to an Ising Hamiltonian, then solved using QAOA (Quantum Approximate Optimization Algorithm) on IBM Quantum hardware or local simulators.</p>
                    
                    <p><strong>Step 4: Result Processing</strong><br>
                    Quantum bitstring results are decoded into ranked root-cause hypotheses with confidence scores, coverage metrics, and quality indicators.</p>
                </div>

                <h3>📦 Technology Stack</h3>
                <div class="concept-grid">
                    <div class="concept-card">
                        <strong>Python 3.10+</strong>
                        <p>Primary programming language for the entire stack</p>
                    </div>
                    <div class="concept-card">
                        <strong>Qiskit</strong>
                        <p>Quantum SDK for QAOA, QUBO→Ising encoding, and IBM Runtime integration</p>
                    </div>
                    <div class="concept-card">
                        <strong>FastAPI</strong>
                        <p>Modern web framework for high-performance API with automatic OpenAPI documentation</p>
                    </div>
                    <div class="concept-card">
                        <strong>Pydantic</strong>
                        <p>Type-safe data validation and serialization</p>
                    </div>
                </div>

                <h3>🏛️ Repository Structure</h3>
                <div class="highlight-box">
                    <pre style="background: #f8f9fa; padding: 15px; border-radius: 4px; overflow-x: auto; font-family: 'Courier New', monospace; font-size: 0.9em;">
src/psq/
├── api/          # HTTP interface (FastAPI endpoints)
├── service/      # Business logic orchestration
├── qubo/         # QUBO formulation and encoding
├── quantum/      # QAOA solver and backend management
└── data/        # Data models and ingestion
                    </pre>
                </div>

                <h3>🔌 Integration Points</h3>
                <ul>
                    <li><strong>SAP Systems</strong> - Integrates with SAP Asset Intelligence Network (AIN), Plant Maintenance (PM), and Manufacturing Execution Systems (MES) via REST API</li>
                    <li><strong>IBM Quantum</strong> - Connects to IBM Quantum Runtime for hardware execution or uses local Qiskit Aer simulators for development</li>
                    <li><strong>Enterprise Systems</strong> - Designed as a sidecar service that can be deployed alongside existing plant management systems</li>
                </ul>

                <h3>⚙️ Key Design Principles</h3>
                <ul>
                    <li><strong>Separation of Concerns</strong> - Each layer has a single, well-defined responsibility</li>
                    <li><strong>Configuration Over Code</strong> - All settings externalized via environment variables</li>
                    <li><strong>Graceful Degradation</strong> - Automatic fallback to simulators when quantum hardware is unavailable</li>
                    <li><strong>Observability</strong> - Comprehensive structured logging and metrics throughout</li>
                </ul>
            </div>
        </div>

        <div class="nav-links">
            <a href="/docs">📚 Interactive API Documentation</a>
            <a href="/health">🏥 Health Check</a>
            <a href="https://github.com" target="_blank">📖 View on GitHub</a>
        </div>
    </div>
</body>
</html>
"""


@app.post(
    "/diagnose-plant-anomaly",
    response_model=QuboRootCauseResult,
    status_code=status.HTTP_200_OK,
    summary="Diagnose plant sensor anomalies",
    description="Accepts anomaly data and returns ranked root-cause hypotheses using QAOA optimization",
)
async def diagnose_plant_anomaly(request: QuboRootCauseRequest) -> QuboRootCauseResult:
    """
    Main endpoint for plant sensor root-cause diagnosis.
    
    Args:
        request: QuboRootCauseRequest with anomaly data and patterns
    
    Returns:
        QuboRootCauseResult with ranked solutions and metadata
    
    Raises:
        HTTPException: 400 for validation errors, 503 for backend unavailability
    """
    try:
        logger.info(
            "Received diagnosis request",
            extra={"anomaly_id": request.anomaly_id, "plant_id": request.plant_id}
        )
        
        # Load configuration
        service_config = load_config()
        
        # Execute diagnosis
        result = diagnose_anomaly(
            request=request,
            qaoa_config=service_config.qaoa,
            service_config=service_config,
        )
        
        logger.info(
            "Diagnosis completed",
            extra={
                "anomaly_id": result.anomaly_id,
                "num_solutions": len(result.solutions),
            }
        )
        
        return result
    
    except ValueError as e:
        logger.warning("Validation error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}",
        )
    
    except RuntimeError as e:
        logger.error("Backend error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Quantum backend unavailable: {str(e)}",
        )
    
    except Exception as e:
        logger.exception("Unexpected error during diagnosis")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@app.get("/health", summary="Health check", description="Check service health and backend availability")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Service status and backend availability
    """
    # TODO: Implement health check logic
    # - Check quantum backend connectivity
    # - Verify configuration is valid
    # - Return status information
    
    return {
        "status": "healthy",
        "version": "0.1.0",
        "backend_available": False,  # TODO: Check actual backend
    }


@app.get("/", response_class=HTMLResponse, summary="Root endpoint", description="Service information and project description")
async def root():
    """
    Root endpoint displaying detailed project description and information.
    
    Returns a comprehensive HTML page explaining:
    - What the project is
    - The problem it solves
    - How it works
    - Who it's for
    - Key concepts
    - Real-world examples
    """
    return PROJECT_DESCRIPTION_HTML

