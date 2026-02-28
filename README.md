# Post-Quantum Key Exchange Performance Analyzer ⚛️

## The Final Locked Definition
> *A laptop-based quantum simulation framework using Qiskit Aer that evaluates the vulnerability of classical key exchange algorithms under quantum attacks (Shor and Grover), and analyzes why post-quantum cryptographic schemes remain secure, using performance, scalability, and security metrics.*

---

## 🎯 1. Problem Identification
Modern secure communications rely heavily on public-key cryptosystems like RSA and Diffie-Hellman, which base their security on prime factorization and discrete logarithms. However, Shor’s algorithm can solve both in polynomial time on a quantum computer. Grover's algorithm provides a quadratic speedup for searching symmetric keys. This means the transition to Post-Quantum Cryptography (PQC) is a mathematical necessity.

---

## 🚀 2. Objective Definition
This project demonstrates **why classical key exchange breaks under quantum assumptions** and motivates the transition to post-quantum key exchange (lattice-based/hash-based). It simulates quantum attacks (Shor’s and Grover’s algorithms) on classical baselines to extract real metrics like qubit count, circuit depth, simulation time, and success probability.

---

## 📁 3. Implementation & Architecture
This is a robust, modular Python package designed for high-quality hackathon/research deliverables.

### Directory Structure
```text
.
├── src/
│   ├── analyzer/     # Scaling logic, metric calculations, and data generators for UI
│   ├── classical/    # Classical RSA and brute force baselines
│   ├── quantum/      # Qiskit circuit builders (Shor, Grover, Noise Simulator)
│   └── __init__.py
├── tests/            # Pytest test suite governing each module
├── ui/
│   └── app.py        # Interactive Streamlit Dashboard (Premium Dark Theme)
├── requirements.txt
└── README.md
```

---

## 🛠️ 4. Setup Instructions

1. **Clone the repository and navigate to the root directory.**
2. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Launch the Premium Performance Analyzer Dashboard:**
   ```bash
   streamlit run ui/app.py
   ```
   > The dashboard is fully self-contained. You can interact with the quantum simulations, view circuit diagrams, and analyze 3D noise degradation surfaces directly via the browser.

---

## 📚 5. Deep Dive: How to Run and Test Each Module Independently

While the Streamlit Dashboard (`ui/app.py`) is the primary way to interact with the project, you can also import and run the core Python modules programmatically. This proves the underlying mathematical integrity.

### 5.1 The Classical Module (`src/classical/`)
This module provides the classical baseline algorithms that quantum computers seek to break.

* **`rsa.py`**: Generates RSA keypairs and simulates classical brute-force prime factorization (trial division).
  * **How to run:**
    ```python
    from src.classical.rsa import classical_factorization, generate_keypair
    public, private = generate_keypair(61, 53)
    print(f"Public Key: {public}")
    
    # Simulate classical factorization of 15
    f1, f2, time_taken, iters = classical_factorization(15)
    print(f"Factors: {f1}, {f2} in {iters} iterations")
    ```
* **`symmetric.py`**: Simulates classical brute-force search against a symmetric key space (representing AES).
  * **How to run:**
    ```python
    from src.classical.symmetric import classical_symmetric_search
    # Search for target '5' in a 3-bit space (0 to 7)
    target, time_taken, iters = classical_symmetric_search(5, 3)
    print(f"Found target in {iters} iterations")
    ```

### 5.2 The Quantum Module (`src/quantum/`)
This module uses Qiskit to build and simulate the quantum circuits that execute Shor's and Grover's algorithms.

* **`shor.py` & `grover.py`**: Parametrized circuit builders.
  * **How to run Shor's:**
    ```python
    from src.quantum.shor import build_shor_circuit
    from src.quantum.simulator import simulate_circuit
    
    # Build circuit to factor N=15 using coprime a=7
    qc = build_shor_circuit(n=15, a=7)
    results = simulate_circuit(qc)
    print("Shor's Metrics:", results['metrics'])
    ```
  * **How to run Grover's:**
    ```python
    from src.quantum.grover import build_grover_circuit
    from src.quantum.simulator import simulate_circuit
    
    # Build 3-qubit circuit to search for State '101'
    qc = build_grover_circuit(num_qubits=3, target_state="101")
    results = simulate_circuit(qc)
    print("Target Probability:", results['probabilities'].get("101"))
    ```
* **`noise.py`**: Injects realistic NISQ-era hardware noise (depolarizing, bit flip, phase flip).

### 5.3 The Analyzer Module (`src/analyzer/`)
Calculates mathematical scaling complexities and generates data for 3D heatmaps and radar charts.

* **`scaling.py`**: Defines the asymptotic scaling curves. O(e^(c*logN^1/3*loglogN^2/3)) for classical GNFS vs O(N^3) for Shor's.
* **`comparison.py`**: Generates head-to-head metrics comparing RSA, AES, Kyber (Lattices), and SPHINCS+ (Hashes).

---

## 🧪 6. Testing the Integrity of the Cryptography

Testing is crucial to verify that the quantum physics simulated here are mathematically sound. 
The project includes an automatic test suite powered by `pytest`.

### Running the Entire Test Suite
From the root directory, simply run:
```bash
pytest tests/ -v
```
You should see 17 passing tests.

### What the Tests Prove (Cryptographic Integrity)
By running the `tests/` directory, you are statistically validating the cryptographic integrity of the system:

1. **`test_classical.py`**: Proves that the classical baseline (RSA factorization and Brute Force search) always yields the mathematically correct factor/target. It confirms that the classical time complexity is growing correctly.
2. **`test_quantum.py`**: Proves that Grover's search reliably amplifies the probability of the *correct* target state (e.g., >80% probability of finding '11' in a 2-qubit space). It also proves that injecting error models (Noise) significantly drops the success rate.
3. **`test_comparison.py`**: Proves that the estimated Quantum Speedup (the ratio of classical operations to quantum operations) strictly increases as key sizes grow, confirming polynomial vs exponential scaling.

---

## 🛡️ 7. Analyzing Cryptographic Integrity & The Post-Quantum Solution

When evaluating the dashboard and source code, observe how the integrity of classical cryptography fails under quantum scrutiny, and why Post-Quantum algorithms survive:

### ❌ The Fall of Classical Integrity (RSA / DH / ECC)
Classical algorithms guard data integrity based on the hardness of discrete logarithms or factoring. Because a quantum computer handles superpositions, **Shor's Algorithm** evaluates global properties of periodic functions. Thus, the integrity of an RSA-2048 key drops from requiring billions of years classically, to just a few hours quantumly. 
* **See this in the UI:** Look at the "Performance & Scaling" tab to watch the exponential gap between Classical and Quantum scaling collapse.

### ❓ The Weakening of Symmetric Integrity (AES / ChaCha20)
**Grover's Algorithm** quadratically speeds up unstructured search. The integrity of an AES-128 key is cut in half to an effective 64-bits of security.
* **See this in the UI:** Look at the "Live Attack Simulation" tab. See how Grover's easily amplifies the target state. The defense is simply doubling the key size (AES-256).

### ✅ The Rise of Post-Quantum Integrity (Lattices & Hashes)
Post-Quantum Cryptography (PQC) abandons factoring and logarithms.
* **Lattice-Based (Kyber/Dilithium):** Rely on the *Learning With Errors (LWE)* problem. To break this, an attacker must find the shortest vector in a chaotic, multi-dimensional grid. Quantum computers offer no known speedup here. 
* **Hash-Based (SPHINCS+):** Rely solely on hashing math. Doubling the hash size permanently stops Grover's algorithm. 
* **See this in the UI:** Look at the "Post-Quantum Security Shield" tab to see the radar charts and gauge cards proving that NIST standards FIPS 203, 204, and 205 maintain 100% of their cryptographic integrity against a quantum attack.
