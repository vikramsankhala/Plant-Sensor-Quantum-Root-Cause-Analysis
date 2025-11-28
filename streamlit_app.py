"""
Streamlit application for Plant Sensor Quantum Root-Cause Analysis.

Provides a user-friendly web interface for diagnosing plant sensor anomalies
using quantum computing optimization.
"""

import streamlit as st
import json
from typing import List, Dict
from psq.data.schemas import (
    SensorAbnormal,
    RootCausePattern,
    QuboRootCauseRequest,
)
from psq.config import load_config
from psq.service.orchestrator import diagnose_anomaly

# Page configuration
st.set_page_config(
    page_title="Plant Sensor Quantum Root-Cause Analysis",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🌿 Plant Sensor Quantum Root-Cause Analysis</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Quantum-Powered Industrial Diagnostics Service</p>', unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.subheader("QUBO Hyperparameters")
    alpha = st.slider("Alpha (Anomaly Coverage)", 0.1, 5.0, 1.0, 0.1)
    beta = st.slider("Beta (Pattern Parsimony)", 0.1, 5.0, 1.0, 0.1)
    gamma = st.slider("Gamma (Consistency)", 0.1, 5.0, 1.0, 0.1)
    
    st.subheader("QAOA Settings")
    qaoa_depth = st.slider("QAOA Depth (p)", 1, 5, 2)
    shots = st.selectbox("Measurement Shots", [256, 512, 1024, 2048], index=2)
    
    st.subheader("Backend Selection")
    backend_type = st.radio(
        "Backend Type",
        ["Simulator", "IBM Quantum"],
        help="Simulator is free and fast. IBM Quantum requires credentials."
    )

# Main content tabs
tab1, tab2, tab3 = st.tabs(["🔍 Diagnosis", "📊 About", "📖 Documentation"])

with tab1:
    st.header("Plant Sensor Anomaly Diagnosis")
    
    # Input section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Anomaly Information")
        anomaly_id = st.text_input("Anomaly ID", value="ANOM_2024_001")
        plant_id = st.text_input("Plant ID", value="PLANT_A")
    
    with col2:
        st.subheader("Quick Start")
        if st.button("📋 Load Example Data"):
            st.session_state.example_loaded = True
            st.rerun()
    
    # Sensor input section
    st.subheader("Abnormal Sensors")
    st.markdown("Add sensors showing abnormal readings with their severity scores.")
    
    if 'sensors' not in st.session_state:
        st.session_state.sensors = []
    if 'patterns' not in st.session_state:
        st.session_state.patterns = []
    if 'example_loaded' in st.session_state and st.session_state.example_loaded:
        st.session_state.sensors = [
            {"sensor_id": "TEMP_001", "severity": 2.5},
            {"sensor_id": "PRESSURE_001", "severity": 3.0},
            {"sensor_id": "FLOW_001", "severity": 1.8},
        ]
        st.session_state.patterns = [
            {
                "pattern_id": "PUMP_CAVITATION",
                "description": "Pump cavitation causing pressure fluctuations",
                "affected_sensors": ["PRESSURE_001", "FLOW_001"],
            },
            {
                "pattern_id": "BEARING_WEAR",
                "description": "Bearing wear causing temperature rise",
                "affected_sensors": ["TEMP_001", "VIBRATION_001"],
            },
        ]
        st.session_state.example_loaded = False
    
    # Sensor input form
    with st.expander("➕ Add Sensor", expanded=False):
        sensor_col1, sensor_col2 = st.columns(2)
        with sensor_col1:
            new_sensor_id = st.text_input("Sensor ID", key="new_sensor_id")
        with sensor_col2:
            new_sensor_severity = st.number_input("Severity", min_value=0.0, max_value=10.0, value=1.0, step=0.1, key="new_sensor_severity")
        
        if st.button("Add Sensor"):
            if new_sensor_id:
                st.session_state.sensors.append({
                    "sensor_id": new_sensor_id,
                    "severity": float(new_sensor_severity)
                })
                st.rerun()
    
    # Display sensors
    if st.session_state.sensors:
        sensor_df_data = []
        for i, sensor in enumerate(st.session_state.sensors):
            sensor_df_data.append({
                "Sensor ID": sensor["sensor_id"],
                "Severity": sensor["severity"],
                "Actions": i
            })
        
        import pandas as pd
        sensor_df = pd.DataFrame(sensor_df_data)
        
        for idx, row in sensor_df.iterrows():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{row['Sensor ID']}** - Severity: {row['Severity']}")
            with col3:
                if st.button("🗑️", key=f"del_sensor_{idx}"):
                    st.session_state.sensors.pop(idx)
                    st.rerun()
    else:
        st.info("No sensors added yet. Click 'Add Sensor' to add abnormal sensors.")
    
    # Pattern input section
    st.subheader("Root-Cause Patterns")
    st.markdown("Define known failure patterns and their affected sensors.")
    
    with st.expander("➕ Add Pattern", expanded=False):
        pattern_id = st.text_input("Pattern ID", key="new_pattern_id")
        pattern_desc = st.text_area("Description", key="new_pattern_desc")
        pattern_sensors = st.text_input(
            "Affected Sensors (comma-separated)",
            key="new_pattern_sensors",
            help="Enter sensor IDs separated by commas, e.g., TEMP_001, PRESSURE_001"
        )
        
        if st.button("Add Pattern"):
            if pattern_id and pattern_sensors:
                sensor_list = [s.strip() for s in pattern_sensors.split(",")]
                st.session_state.patterns.append({
                    "pattern_id": pattern_id,
                    "description": pattern_desc or f"Pattern: {pattern_id}",
                    "affected_sensors": sensor_list,
                })
                st.rerun()
    
    # Display patterns
    if st.session_state.patterns:
        for i, pattern in enumerate(st.session_state.patterns):
            with st.expander(f"🔧 {pattern['pattern_id']}", expanded=False):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**Description:** {pattern['description']}")
                    st.write(f"**Affected Sensors:** {', '.join(pattern['affected_sensors'])}")
                with col2:
                    if st.button("🗑️ Delete", key=f"del_pattern_{i}"):
                        st.session_state.patterns.pop(i)
                        st.rerun()
    else:
        st.info("No patterns added yet. Click 'Add Pattern' to add root-cause patterns.")
    
    # Diagnosis button
    st.divider()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        diagnose_button = st.button(
            "🚀 Run Quantum Diagnosis",
            type="primary",
            use_container_width=True,
            disabled=len(st.session_state.sensors) == 0 or len(st.session_state.patterns) == 0
        )
    
    if diagnose_button:
        if len(st.session_state.sensors) == 0:
            st.error("Please add at least one abnormal sensor.")
        elif len(st.session_state.patterns) == 0:
            st.error("Please add at least one root-cause pattern.")
        else:
            with st.spinner("Running quantum optimization... This may take a moment."):
                try:
                    # Convert to Pydantic models
                    sensors = [
                        SensorAbnormal(**sensor) for sensor in st.session_state.sensors
                    ]
                    patterns = [
                        RootCausePattern(**pattern) for pattern in st.session_state.patterns
                    ]
                    
                    # Create request
                    request = QuboRootCauseRequest(
                        anomaly_id=anomaly_id,
                        plant_id=plant_id,
                        abnormal_sensors=sensors,
                        patterns=patterns,
                        alpha=alpha,
                        beta=beta,
                        gamma=gamma,
                    )
                    
                    # Load config and update
                    config = load_config()
                    config.qaoa.depth = qaoa_depth
                    config.qaoa.shots = shots
                    config.backend.backend_type = "simulator" if backend_type == "Simulator" else "ibm_quantum"
                    
                    # Run diagnosis
                    result = diagnose_anomaly(
                        request=request,
                        qaoa_config=config.qaoa,
                        service_config=config,
                    )
                    
                    # Display results
                    st.success("✅ Diagnosis completed!")
                    
                    st.subheader("📊 Results")
                    
                    # Top solution
                    if result.solutions:
                        top_solution = result.solutions[0]
                        st.markdown(f"""
                        <div class="info-box">
                            <h3>🎯 Top Root-Cause Hypothesis</h3>
                            <p><strong>Selected Patterns:</strong> {', '.join(top_solution.selected_patterns)}</p>
                            <p><strong>Covered Sensors:</strong> {', '.join(top_solution.covered_sensors)}</p>
                            <p><strong>Confidence Score:</strong> {top_solution.confidence_score:.2f}%</p>
                            <p><strong>Energy:</strong> {top_solution.energy:.4f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # All solutions
                        st.subheader("📋 All Solutions (Ranked)")
                        solutions_data = []
                        for i, sol in enumerate(result.solutions, 1):
                            solutions_data.append({
                                "Rank": i,
                                "Patterns": ", ".join(sol.selected_patterns),
                                "Covered Sensors": len(sol.covered_sensors),
                                "Confidence": f"{sol.confidence_score:.2f}%",
                                "Energy": f"{sol.energy:.4f}",
                            })
                        st.dataframe(pd.DataFrame(solutions_data), use_container_width=True)
                    
                    # Quality metrics
                    st.subheader("📈 Quality Metrics")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Coverage Rate", f"{result.quality_metrics.coverage_rate:.1f}%")
                    with col2:
                        st.metric("Avg Pattern Count", f"{result.quality_metrics.average_pattern_count:.2f}")
                    with col3:
                        st.metric("Residual Anomalies", len(result.quality_metrics.residual_anomalies))
                    
                    if result.quality_metrics.residual_anomalies:
                        st.warning(f"⚠️ Unexplained sensors: {', '.join(result.quality_metrics.residual_anomalies)}")
                    
                    # Backend metadata
                    with st.expander("🔧 Execution Details"):
                        st.json({
                            "backend": result.backend_metadata.backend_name,
                            "backend_type": result.backend_metadata.backend_type,
                            "execution_time": f"{result.backend_metadata.execution_time_seconds:.2f}s",
                            "shots": result.backend_metadata.shots,
                            "qaoa_depth": result.backend_metadata.qaoa_depth,
                        })
                
                except NotImplementedError as e:
                    st.error(f"⚠️ Feature not yet implemented: {str(e)}")
                    st.info("""
                    The core quantum optimization logic is still being developed.
                    The architecture is in place, but the QUBO construction and QAOA execution
                    modules need to be implemented. See the ARCHITECTURE.md for details.
                    """)
                except Exception as e:
                    st.error(f"❌ Error during diagnosis: {str(e)}")
                    st.exception(e)

with tab2:
    st.header("About This Project")
    
    st.markdown("""
    ### What is This Project?
    
    This project is a **quantum computing service** that helps industrial plants quickly identify 
    the root causes of equipment problems by analyzing sensor data.
    
    ### The Problem It Solves
    
    In industrial plants, hundreds or thousands of sensors constantly monitor equipment. When 
    something goes wrong, multiple sensors often show abnormal readings simultaneously. This service 
    uses **quantum computing** to analyze all possibilities simultaneously and find the most likely 
    root cause faster.
    """)
    
    st.divider()
    
    st.subheader("🏗️ Technical Architecture")
    
    st.markdown("""
    The system follows a **layered architecture** with clear separation of concerns:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **1. API Layer (FastAPI)**
        - Handles HTTP requests and responses
        - Input validation and serialization
        - Error handling and logging
        
        **2. Service Layer**
        - Orchestrates the diagnosis workflow
        - Coordinates between layers
        - Manages configuration
        """)
    
    with col2:
        st.markdown("""
        **3. QUBO Layer**
        - Converts sensor data to optimization problems
        - Builds energy functions
        - Encodes to Ising Hamiltonians
        
        **4. Quantum Layer**
        - Executes QAOA algorithm
        - Manages quantum backends
        - Handles simulator/hardware selection
        """)
    
    st.markdown("""
    **5. Data Layer**
    - Pydantic models for type safety
    - Data validation and transformation
    - Pattern library management
    """)
    
    st.divider()
    
    st.subheader("⚛️ Quantum vs Classical Computing")
    
    st.markdown("""
    ### Fundamental Differences
    """)
    
    comparison_data = {
        "Aspect": ["Computation Model", "Problem Exploration", "State Representation", "Parallelism", "Best For"],
        "Classical Computing": [
            "Binary bits (0 or 1)",
            "Sequential evaluation",
            "Single state at a time",
            "Simulated parallelism",
            "Deterministic problems, large datasets"
        ],
        "Quantum Computing": [
            "Quantum bits (superposition)",
            "Simultaneous exploration",
            "Multiple states simultaneously",
            "True quantum parallelism",
            "Optimization, search, simulation"
        ]
    }
    
    import pandas as pd
    st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)
    
    st.markdown("""
    **Key Insight**: Quantum computers can explore many possible solutions at once using **quantum superposition**, 
    while classical computers must check solutions one at a time. This gives quantum algorithms a potential 
    advantage for combinatorial optimization problems like root-cause diagnosis.
    """)
    
    st.divider()
    
    st.subheader("🔬 Quantum vs Classical Solvers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Classical Solvers
        
        **Simulated Annealing**
        - Randomly explores solution space
        - Gradually "cools down" to find minima
        - Can get stuck in local optima
        - Time: O(n²) to O(2ⁿ) depending on problem
        
        **Genetic Algorithms**
        - Evolves population of solutions
        - Uses mutation and crossover
        - Good for complex landscapes
        - Requires many iterations
        
        **Integer Programming (Gurobi, CPLEX)**
        - Exact solutions for small problems
        - Branch-and-bound techniques
        - Exponential time for hard problems
        - Limited by problem size
        """)
    
    with col2:
        st.markdown("""
        ### Quantum Solvers (QAOA)
        
        **Quantum Approximate Optimization**
        - Explores solution space in superposition
        - Uses quantum interference
        - Can escape local optima naturally
        - Potential polynomial speedup
        
        **Advantages:**
        - ✅ Parallel exploration of solution space
        - ✅ Quantum tunneling through barriers
        - ✅ Natural handling of correlations
        - ✅ Better for highly constrained problems
        
        **Current Limitations:**
        - ⚠️ Limited qubit count (current hardware)
        - ⚠️ Noise and error rates
        - ⚠️ Requires quantum-classical hybrid approach
        """)
    
    st.info("""
    **For Root-Cause Analysis**: Quantum solvers excel when you have many sensors and patterns with complex 
    interdependencies. Classical solvers work well for small problems but struggle with the exponential 
    search space as problem size grows.
    """)
    
    st.divider()
    
    st.subheader("🧮 Quantum vs Classical Algorithms")
    
    st.markdown("""
    ### Algorithm Comparison for Root-Cause Diagnosis
    """)
    
    algorithm_comparison = {
        "Algorithm Type": [
            "Brute Force (Classical)",
            "Greedy Search (Classical)",
            "Dynamic Programming (Classical)",
            "QAOA (Quantum)"
        ],
        "Approach": [
            "Check all combinations",
            "Make locally optimal choices",
            "Break into subproblems",
            "Quantum superposition + optimization"
        ],
        "Time Complexity": [
            "O(2ⁿ) - Exponential",
            "O(n²) - Polynomial",
            "O(n²) to O(2ⁿ)",
            "O(poly(n)) - Potential speedup"
        ],
        "Best For": [
            "Small problems (<20 variables)",
            "Problems with optimal substructure",
            "Problems with overlapping subproblems",
            "Combinatorial optimization"
        ]
    }
    
    st.dataframe(pd.DataFrame(algorithm_comparison), use_container_width=True, hide_index=True)
    
    st.markdown("""
    ### Why QAOA for This Problem?
    
    1. **Combinatorial Nature**: Root-cause diagnosis involves selecting combinations of patterns - 
       exactly what QAOA is designed for.
    
    2. **Multiple Objectives**: We balance anomaly coverage, pattern parsimony, and consistency - 
       QAOA's variational approach handles this naturally.
    
    3. **Correlations**: Sensors and patterns have complex relationships - quantum entanglement 
       can capture these correlations better than classical methods.
    
    4. **Scalability**: As plants add more sensors and patterns, classical methods slow down 
       exponentially, while quantum methods may maintain polynomial scaling.
    """)
    
    st.divider()
    
    st.subheader("🔄 How It Works")
    
    st.markdown("""
    1. **Input**: You provide abnormal sensors and known failure patterns
    2. **QUBO Construction**: The system converts this into a Quadratic Unconstrained Binary Optimization problem
    3. **Ising Encoding**: QUBO is transformed into an Ising Hamiltonian (quantum physics formulation)
    4. **Quantum Solving**: QAOA algorithm runs on quantum hardware/simulator
    5. **Results**: Quantum measurements are decoded into ranked root-cause hypotheses with confidence scores
    """)
    
    st.divider()
    
    st.subheader("💻 Technology Stack")
    
    st.markdown("""
    - **Python 3.10+** - Primary language
    - **Qiskit** - Quantum SDK for QAOA and IBM Quantum integration
    - **FastAPI** - REST API backend
    - **Streamlit** - Web interface
    - **Pydantic** - Type-safe data validation
    - **IBM Quantum** - Quantum hardware access (optional)
    - **Qiskit Aer** - Quantum simulators for development
    """)
    
    st.divider()
    
    st.subheader("📚 Repository")
    
    st.markdown("""
    [GitHub Repository](https://github.com/vikramsankhala/Plant-Sensor-Quantum-Root-Cause-Analysis)
    
    For detailed architecture documentation, see [ARCHITECTURE.md](https://github.com/vikramsankhala/Plant-Sensor-Quantum-Root-Cause-Analysis/blob/main/ARCHITECTURE.md)
    """)

with tab3:
    st.header("Documentation")
    
    st.markdown("""
    ### Quick Start Guide
    
    1. **Add Abnormal Sensors**: Click "Add Sensor" and enter sensor IDs with severity scores
    2. **Add Root-Cause Patterns**: Define known failure patterns and their affected sensors
    3. **Configure Parameters**: Adjust QUBO hyperparameters and QAOA settings in the sidebar
    4. **Run Diagnosis**: Click "Run Quantum Diagnosis" to get results
    
    ### Understanding Results
    
    - **Confidence Score**: Higher is better (0-100%)
    - **Energy**: Lower is better (QUBO energy value)
    - **Coverage Rate**: Percentage of sensors explained by the solution
    - **Residual Anomalies**: Sensors not explained by any pattern
    
    ### Configuration
    
    - **Alpha**: Weight for anomaly coverage (higher = prioritize explaining severe anomalies)
    - **Beta**: Weight for pattern parsimony (higher = prefer fewer patterns)
    - **Gamma**: Weight for consistency (higher = stricter pattern-sensor matching)
    - **QAOA Depth**: Number of layers (higher = more accurate but slower)
    
    For detailed architecture documentation, see [ARCHITECTURE.md](https://github.com/vikramsankhala/Plant-Sensor-Quantum-Root-Cause-Analysis/blob/main/ARCHITECTURE.md)
    """)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>Plant Sensor Quantum Root-Cause Analysis v0.1.0</p>
    <p>Built with ❤️ using Streamlit, Qiskit, and FastAPI</p>
</div>
""", unsafe_allow_html=True)

