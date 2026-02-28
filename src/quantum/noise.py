from qiskit_aer.noise import NoiseModel, depolarizing_error, pauli_error

def get_noise_model(noise_level: float, noise_type: str = 'depolarizing') -> NoiseModel:
    """
    Returns a Qiskit Aer NoiseModel for the specified level and type.
    """
    noise_model = NoiseModel()

    if noise_level <= 0:
         return noise_model

    if noise_type == 'depolarizing':
        error_1q = depolarizing_error(noise_level, 1)
        error_2q = depolarizing_error(noise_level * 2, 2)
        noise_model.add_all_qubit_quantum_error(error_1q, ['u1', 'u2', 'u3', 'h', 'x', 'y', 'z'])
        noise_model.add_all_qubit_quantum_error(error_2q, ['cx', 'cz'])

    elif noise_type == 'bit_flip':
        error_1q = pauli_error([('X', noise_level), ('I', 1 - noise_level)])
        error_2q = error_1q.tensor(error_1q)
        noise_model.add_all_qubit_quantum_error(error_1q, ['u1', 'u2', 'u3', 'h', 'x', 'y', 'z'])
        noise_model.add_all_qubit_quantum_error(error_2q, ['cx', 'cz'])

    elif noise_type == 'phase_flip':
        error_1q = pauli_error([('Z', noise_level), ('I', 1 - noise_level)])
        error_2q = error_1q.tensor(error_1q)
        noise_model.add_all_qubit_quantum_error(error_1q, ['u1', 'u2', 'u3', 'h', 'x', 'y', 'z'])
        noise_model.add_all_qubit_quantum_error(error_2q, ['cx', 'cz'])

    else:
        raise ValueError(f"Unsupported noise type: {noise_type}")

    return noise_model
