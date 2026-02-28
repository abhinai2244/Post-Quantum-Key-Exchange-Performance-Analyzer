# Post-Quantum Key Exchange Performance Analyzer ⚛️

## The Final Locked Definition
> *A laptop-based quantum simulation framework using Qiskit Aer that evaluates the vulnerability of classical key exchange algorithms under quantum attacks (Shor and Grover), and analyzes why post-quantum cryptographic schemes remain secure, using performance, scalability, and security metrics.*

## 1. Problem Identification
Modern secure communications rely heavily on public-key cryptosystems like RSA and Diffie-Hellman, which base their security on prime factorization and discrete logarithms. However, Shor’s algorithm can solve both in polynomial time on a quantum computer. Grover's algorithm provides a quadratic speedup for searching symmetric keys. This means the transition to Post-Quantum Cryptography (PQC) is a mathematical necessity.

## 2. Objective Definition
This project demonstrates **why classical key exchange breaks under quantum assumptions** and motivates the transition to post-quantum key exchange (lattice-based/hash-based). It simulates quantum attacks (Shor’s and Grover’s algorithms) on classical baselines to extract real metrics like qubit count, circuit depth, simulation time, and success probability.

## 3. Implementation & Architecture
This is a robust, modular Python package designed for high-quality hackathon/research deliverables.

### Directory Structure
```text
.
├── src/
│   ├── analyzer/     # Scaling logic and metric calculations
│   ├── classical/    # Classical RSA and brute force baselines
│   ├── quantum/      # Qiskit circuit builders (Shor, Grover, Noise)
│   └── __init__.py
├── tests/            # Pytest suite
├── ui/
│   └── app.py        # Interactive Streamlit Dashboard
├── requirements.txt
└── README.md
```

### Key Features
- **Strict Modular Python Package:** Clean separation of concerns (Classical vs. Quantum vs. Analysis). Can easily be expanded to expose a FastAPI backend in the future.
- **Parameterized Quantum Circuits:** Supports Shor's algorithm (N=15, 21) and Grover's algorithm (variable oracle sizes and iterations).
- **NISQ Noise Models:** Incorporates Qiskit Aer depolarizing noise models to demonstrate real-world quantum limitations (Noisy Intermediate-Scale Quantum era).
- **Comprehensive Test Suite:** Ensures reliability of quantum logic and classical baselines.

## 4. Setup Instructions

1. **Clone the repository and navigate to the root directory.**
2. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Test Suite (Optional but recommended):**
   ```bash
   pytest tests/
   ```
4. **Launch the Performance Analyzer Dashboard:**
   ```bash
   streamlit run ui/app.py
   ```

## 5. Result Analysis and Conclusion
The dashboard presents analytical comparisons:
- **Asymptotic Scaling:** Shows the transition from exponential classical time to polynomial/sub-exponential quantum time.
- **Noise Analysis:** Demonstrates that as depolarizing noise increases, the success probability of Grover's algorithm quickly degrades to random guessing, illustrating the need for fault-tolerant quantum computers (QEC).
- **Post-Quantum Resistance:** Explains theoretically why Lattice-based and Hash-based signatures remain exponentially hard against these quantum attacks.
