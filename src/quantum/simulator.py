import time
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
import numpy as np

def simulate_circuit(circuit: QuantumCircuit, noise_model: NoiseModel = None, shots: int = 1024) -> dict:
    """
    Simulates a given QuantumCircuit using Qiskit AerSimulator.
    Calculates execution time, depth, gate counts, and returns probability distribution.
    """
    simulator = AerSimulator()

    # Transpile the circuit to unroll complex gates and calculate exact depth
    transpiled_circuit = transpile(circuit, simulator)

    start_time = time.time()
    
    if noise_model is not None and len(noise_model.noise_instructions) > 0:
        # Pass the noise model through the backend options
        job = simulator.run(transpiled_circuit, shots=shots, noise_model=noise_model)
    else:
        job = simulator.run(transpiled_circuit, shots=shots)

    result = job.result()
    exec_time = time.time() - start_time
    counts = result.get_counts(transpiled_circuit)

    # Convert counts to probabilities
    probabilities = {state: count / shots for state, count in counts.items()}

    # Calculate metrics
    depth = transpiled_circuit.depth()
    gate_counts = dict(transpiled_circuit.count_ops())
    total_gates = sum(gate_counts.values())
    qubits_required = transpiled_circuit.num_qubits

    return {
        "probabilities": probabilities,
        "counts": counts,
        "metrics": {
            "execution_time_seconds": exec_time,
            "depth": depth,
            "total_gates": total_gates,
            "gate_counts": gate_counts,
            "qubits_required": qubits_required
        }
    }
