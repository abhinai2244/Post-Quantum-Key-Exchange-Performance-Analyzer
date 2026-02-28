import pytest
from src.quantum.shor import build_shor_circuit
from src.quantum.grover import build_grover_circuit
from src.quantum.simulator import simulate_circuit
from src.quantum.noise import get_noise_model

def test_build_shor_circuit_15():
    qc = build_shor_circuit(15, 7)
    # 8 counting qubits, 4 modulo qubits
    assert qc.num_qubits == 12
    # Ensure measurement is set up
    assert qc.num_clbits == 8

def test_build_shor_circuit_21():
    qc = build_shor_circuit(21, 2)
    # 9 counting qubits, 5 modulo qubits
    assert qc.num_qubits == 14
    assert qc.num_clbits == 9

def test_simulate_shor_circuit():
    qc = build_shor_circuit(15, 7)
    results = simulate_circuit(qc, shots=100)
    
    # Check metric dictionary
    assert 'probabilities' in results
    assert 'metrics' in results
    
    metrics = results['metrics']
    assert metrics['depth'] > 0
    assert metrics['total_gates'] > 0
    assert metrics['qubits_required'] == 12

def test_build_grover_circuit():
    qc = build_grover_circuit(3, "101")
    assert qc.num_qubits == 3

def test_simulate_grover_circuit():
    qc = build_grover_circuit(2, "11")
    results = simulate_circuit(qc, shots=512)
    
    probs = results['probabilities']
    # '11' should have high probability
    assert probs.get('11', 0) > 0.8
    
    metrics = results['metrics']
    assert metrics['qubits_required'] == 2
    assert metrics['depth'] > 0

def test_noise_model_generation():
    model = get_noise_model(0.01, 'depolarizing')
    assert len(model.noise_instructions) > 0

def test_zero_noise_model():
    model = get_noise_model(0.0, 'depolarizing')
    assert len(model.noise_instructions) == 0
