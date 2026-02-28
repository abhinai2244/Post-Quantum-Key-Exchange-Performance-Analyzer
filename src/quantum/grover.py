import math
from qiskit import QuantumCircuit
from qiskit.circuit.library import GroverOperator, ZGate
from qiskit.circuit import Gate

def build_grover_oracle(num_qubits: int, target_state: str) -> QuantumCircuit:
    """
    Builds a simple Grover oracle that marks a specific target state.
    """
    if len(target_state) != num_qubits:
        raise ValueError("Target state length must match the number of qubits.")

    qc = QuantumCircuit(num_qubits)

    # Flip the phase of the target state
    for i, bit in enumerate(target_state[::-1]):
        if bit == '0':
            qc.x(i)

    # Multi-controlled Z gate
    qc.h(num_qubits - 1)
    qc.mcx(list(range(num_qubits - 1)), num_qubits - 1)
    qc.h(num_qubits - 1)

    for i, bit in enumerate(target_state[::-1]):
        if bit == '0':
            qc.x(i)

    # Don't convert to Gate because GroverOperator expects a QuantumCircuit or Statevector
    # that exposes num_ancillas, or we can just pass the circuit directly
    return qc


def build_grover_circuit(num_qubits: int, target_state: str, iterations: int = None) -> QuantumCircuit:
    """
    Builds a complete parameterized Grover's Algorithm circuit.
    If iterations is not provided, it uses the optimal integer approximation
    of pi/4 * sqrt(N), where N = 2**num_qubits.
    """
    if iterations is None:
        N = 2 ** num_qubits
        iterations = int(math.pi / 4 * math.sqrt(N))

    oracle = build_grover_oracle(num_qubits, target_state)
    grover_op = GroverOperator(oracle)

    qc = QuantumCircuit(num_qubits, num_qubits)

    # Initialization
    qc.h(range(num_qubits))

    # Apply Grover iterations
    for _ in range(iterations):
        qc.append(grover_op, range(num_qubits))

    # Measurement
    qc.measure(range(num_qubits), range(num_qubits))

    return qc
