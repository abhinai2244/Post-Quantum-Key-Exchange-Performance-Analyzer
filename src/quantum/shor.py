import math
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT

def build_shor_circuit(n: int, a: int = None) -> QuantumCircuit:
    """
    Builds a Shor's algorithm circuit for small integers N (e.g., 15, 21).
    This function implements a simplified, hardcoded version of modular
    exponentiation suitable for small N, primarily to demonstrate the
    circuit depth, qubit count, and quantum scaling behavior.
    """
    if n not in [15, 21]:
        raise ValueError("Only N=15 and N=21 are currently supported for demonstration.")

    if n == 15:
        # Default coprime for N=15 is a=7
        a = 7 if a is None else a
        if a not in [2, 7, 8, 11, 13]:
            raise ValueError(f"'a' must be coprime to {n} and not 1 or 14.")

        # Register sizes
        n_count = 8  # number of counting qubits
        n_mod = 4    # qubits for modulo operations

        qr_count = QuantumRegister(n_count, 'count')
        qr_mod = QuantumRegister(n_mod, 'mod')
        cr = ClassicalRegister(n_count, 'c')
        qc = QuantumCircuit(qr_count, qr_mod, cr)

        # Initialize counting qubits in superposition
        qc.h(qr_count)

        # Initialize the target register to |1>
        qc.x(qr_mod[0])

        # Apply controlled modular exponentiation
        for q in range(n_count):
            power = 2**q
            _append_c_amod15(qc, power, a, qr_count[q], qr_mod)

        # Apply inverse QFT to the counting register
        qc.append(QFT(n_count, do_swaps=False).inverse(), qr_count)

        # Measure
        qc.measure(qr_count, cr)

        return qc

    elif n == 21:
        # For N=21, we use 5 qubits for the target register and 9 for counting
        a = 2 if a is None else a
        if math.gcd(a, 21) != 1:
            raise ValueError(f"'a' must be coprime to {n}")

        n_count = 9
        n_mod = 5

        qr_count = QuantumRegister(n_count, 'count')
        qr_mod = QuantumRegister(n_mod, 'mod')
        cr = ClassicalRegister(n_count, 'c')
        qc = QuantumCircuit(qr_count, qr_mod, cr)

        qc.h(qr_count)
        qc.x(qr_mod[0])

        # Applying a generic, highly-simplified block just to represent the depth
        # Real modular exponentiation for N=21 requires complex synthesis.
        # Here we add dummy CX and CCX gates to approximate the depth and gate counts
        # for a generic controlled multiplier.
        for q in range(n_count):
             # Simulate depth of modular exponentiation block
             for i in range(n_mod - 1):
                 qc.ccx(qr_count[q], qr_mod[i], qr_mod[i+1])
             for i in range(n_mod):
                 qc.cx(qr_count[q], qr_mod[i])

        qc.append(QFT(n_count, do_swaps=False).inverse(), qr_count)
        qc.measure(qr_count, cr)

        return qc


def _append_c_amod15(qc, power, a, control, target):
    """
    Appends the controlled modular exponentiation gates for N=15.
    (Simplified hardcoded operations for common a values)
    """
    if a not in [2, 7, 8, 11, 13]:
        raise ValueError("'a' must be 2, 7, 8, 11 or 13")

    # a = 7
    if a == 7:
        for _ in range(power):
            qc.cx(control, target[0])
            qc.cx(control, target[1])
            qc.cx(control, target[2])
            qc.cx(control, target[3])

    # a = 11
    elif a == 11:
        for _ in range(power):
            qc.cx(control, target[0])
            qc.cx(control, target[2])

    # a = 13
    elif a == 13:
        for _ in range(power):
            qc.cx(control, target[0])
            qc.cx(control, target[1])
            qc.cx(control, target[3])

    # a = 8
    elif a == 8:
        for _ in range(power):
            qc.cx(control, target[0])
            qc.cx(control, target[1])

    # a = 2
    elif a == 2:
        for _ in range(power):
            qc.cx(control, target[0])
            qc.cx(control, target[2])
            qc.cx(control, target[3])
