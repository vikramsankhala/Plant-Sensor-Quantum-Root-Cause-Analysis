"""
QUBO to Ising Hamiltonian transformation.

This module performs the critical transformation from QUBO representation
(natural for combinatorial optimization problems) to Ising model formulation
(natural for quantum hardware).
"""

from typing import Dict, Tuple
from qiskit.quantum_info import SparsePauliOp


def qubo_to_ising_hamiltonian(
    qubo_dict: Dict[Tuple[str, str], float],
    var_index: Dict[str, int],
) -> SparsePauliOp:
    """
    Convert QUBO dictionary to Ising Hamiltonian (SparsePauliOp).
    
    Transformation: binary variable b_i ∈ {0,1} maps to spin s_i ∈ {-1,+1}
    via b_i = (1 + s_i)/2.
    
    The Ising Hamiltonian is: H_C = Σᵢ hᵢ Zᵢ + Σᵢⱼ Jᵢⱼ Zᵢ Zⱼ + constant
    
    Where:
    - hᵢ: Local magnetic field on qubit i
    - Jᵢⱼ: Coupling strength between qubits i and j
    - Zᵢ: Pauli-Z operator on qubit i
    
    Args:
        qubo_dict: QUBO coefficient dictionary mapping (var1, var2) to coefficients
        var_index: Mapping from variable names to qubit indices
    
    Returns:
        SparsePauliOp representing the Ising cost Hamiltonian
    
    Raises:
        ValueError: If variable indices are inconsistent or invalid
    """
    # TODO: Implement QUBO to Ising transformation
    # 1. Extract linear and quadratic terms from QUBO dictionary
    # 2. Apply substitution: b_i = (1 + s_i)/2
    # 3. Expand and collect terms to get Ising coefficients
    # 4. Build SparsePauliOp with:
    #    - Single-qubit Z operators for h_i terms
    #    - Two-qubit ZZ operators for J_ij terms
    #    - Constant offset (can be ignored for optimization)
    # 5. Ensure qubit ordering matches var_index
    
    raise NotImplementedError("QUBO to Ising transformation not yet implemented")


def ising_to_qubo(
    hamiltonian: SparsePauliOp,
    var_index: Dict[str, int],
) -> Dict[Tuple[str, str], float]:
    """
    Convert Ising Hamiltonian back to QUBO form (inverse transformation).
    
    Useful for validation and debugging.
    
    Args:
        hamiltonian: SparsePauliOp Ising Hamiltonian
        var_index: Mapping from qubit indices to variable names
    
    Returns:
        QUBO coefficient dictionary
    """
    # TODO: Implement inverse transformation
    raise NotImplementedError("Ising to QUBO transformation not yet implemented")

