"""
Comparison data generators for the Post-Quantum Key Exchange Performance Analyzer.
Provides structured data for radar charts, threat timelines, speedup calculations,
and multi-dimensional noise heatmaps.
"""

import math
import numpy as np
import pandas as pd
from src.analyzer.scaling import (
    classical_factorization_scaling,
    shor_scaling,
    classical_search_scaling,
    grover_scaling,
)


def generate_algorithm_comparison() -> pd.DataFrame:
    """
    Generates a comparison DataFrame for radar chart visualization.
    Compares RSA, Diffie-Hellman, CRYSTALS-Kyber (Lattice), and SPHINCS+ (Hash)
    across five normalized dimensions (0-100 scale).
    """
    data = {
        "Algorithm": [
            "RSA-2048",
            "Diffie-Hellman",
            "CRYSTALS-Kyber (Lattice)",
            "CRYSTALS-Dilithium (Lattice)",
            "SPHINCS+ (Hash-Based)",
        ],
        "Key Size Efficiency": [30, 35, 85, 70, 40],
        "Classical Security": [90, 85, 95, 95, 95],
        "Quantum Resistance": [5, 5, 95, 95, 98],
        "Performance Speed": [50, 55, 90, 80, 35],
        "Standardization Maturity": [100, 100, 90, 90, 85],
    }
    return pd.DataFrame(data)


def generate_threat_timeline() -> pd.DataFrame:
    """
    Generates a DataFrame of significant milestones in cryptography and
    quantum computing for a visual timeline chart.
    """
    milestones = [
        {
            "Year": 1977,
            "Event": "RSA Published",
            "Category": "Classical Crypto",
            "Description": "Rivest, Shamir, and Adleman publish the RSA algorithm, founding modern public-key cryptography.",
            "Impact": "Foundation",
        },
        {
            "Year": 1976,
            "Event": "Diffie-Hellman Key Exchange",
            "Category": "Classical Crypto",
            "Description": "Whitfield Diffie and Martin Hellman publish the first practical key exchange protocol.",
            "Impact": "Foundation",
        },
        {
            "Year": 1994,
            "Event": "Shor's Algorithm",
            "Category": "Quantum Threat",
            "Description": "Peter Shor discovers a polynomial-time quantum algorithm for integer factorization, threatening RSA.",
            "Impact": "Critical Threat",
        },
        {
            "Year": 1996,
            "Event": "Grover's Algorithm",
            "Category": "Quantum Threat",
            "Description": "Lov Grover discovers a quadratic speedup for unstructured search, weakening symmetric crypto.",
            "Impact": "Moderate Threat",
        },
        {
            "Year": 2001,
            "Event": "IBM Factors 15",
            "Category": "Quantum Milestone",
            "Description": "IBM uses a 7-qubit quantum computer to factor 15 into 3×5 using Shor's algorithm.",
            "Impact": "Proof of Concept",
        },
        {
            "Year": 2016,
            "Event": "NIST PQC Competition Begins",
            "Category": "Post-Quantum",
            "Description": "NIST announces the Post-Quantum Cryptography Standardization Process with 69 submissions.",
            "Impact": "Defense Initiated",
        },
        {
            "Year": 2019,
            "Event": "Google Quantum Supremacy",
            "Category": "Quantum Milestone",
            "Description": "Google's Sycamore (53 qubits) demonstrates quantum supremacy on a sampling task.",
            "Impact": "Escalation",
        },
        {
            "Year": 2023,
            "Event": "IBM 1,121-Qubit Condor",
            "Category": "Quantum Milestone",
            "Description": "IBM unveils the 1,121-qubit Condor chip, pushing toward error-corrected quantum computing.",
            "Impact": "Escalation",
        },
        {
            "Year": 2024,
            "Event": "NIST PQC Standards Published",
            "Category": "Post-Quantum",
            "Description": "NIST publishes FIPS 203 (Kyber/ML-KEM), FIPS 204 (Dilithium/ML-DSA), FIPS 205 (SPHINCS+/SLH-DSA).",
            "Impact": "Standard Adopted",
        },
        {
            "Year": 2025,
            "Event": "Global PQC Migration Begins",
            "Category": "Post-Quantum",
            "Description": "Major cloud providers and governments begin mandatory migration to PQC algorithms.",
            "Impact": "Active Defense",
        },
    ]
    df = pd.DataFrame(milestones)
    df = df.sort_values("Year").reset_index(drop=True)
    return df


def generate_speedup_factors(bit_sizes: list[int]) -> pd.DataFrame:
    """
    Calculates exact classical-vs-quantum speedup ratios for given bit sizes.
    Returns a DataFrame with speedup factors for both factorization and search.
    """
    classical_factor = classical_factorization_scaling(bit_sizes)
    quantum_factor = shor_scaling(bit_sizes)
    classical_search = classical_search_scaling(bit_sizes)
    quantum_search = grover_scaling(bit_sizes)

    rows = []
    for i, bits in enumerate(bit_sizes):
        factor_speedup = classical_factor[i] / max(quantum_factor[i], 1)
        
        c_search = classical_search[i]
        q_search = max(quantum_search[i], 1)
        
        # Use integer division for massive ints to avoid Float OverflowError
        if isinstance(c_search, int) and isinstance(q_search, int):
            search_speedup = c_search // q_search
        else:
            search_speedup = c_search / q_search

        rows.append(
            {
                "Key Size (bits)": bits,
                "Classical Factorization (ops)": classical_factor[i],
                "Shor's Algorithm (ops)": quantum_factor[i],
                "Factorization Speedup": factor_speedup,
                "Factorization Speedup (log10)": math.log10(max(factor_speedup, 1)),
                "Classical Search (ops)": c_search,
                "Grover's Algorithm (ops)": q_search,
                "Search Speedup": search_speedup,
                "Search Speedup (log10)": math.log10(max(search_speedup, 1)),
            }
        )
    return pd.DataFrame(rows)


def generate_noise_heatmap_data(
    noise_types: list[str] | None = None,
    noise_levels: list[float] | None = None,
    qubit_counts: list[int] | None = None,
) -> pd.DataFrame:
    """
    Generates a 3D data matrix for noise heatmap visualization.
    Runs Grover simulations across noise types, levels, and qubit counts.
    Returns a flat DataFrame suitable for Plotly heatmap / surface plots.

    Note: This function imports and runs actual quantum simulations, so
    it is designed to be called from the UI layer with a spinner.
    """
    from src.quantum.grover import build_grover_circuit
    from src.quantum.noise import get_noise_model
    from src.quantum.simulator import simulate_circuit

    if noise_types is None:
        noise_types = ["depolarizing", "bit_flip", "phase_flip"]
    if noise_levels is None:
        noise_levels = [0.0, 0.005, 0.01, 0.02, 0.03, 0.05, 0.08, 0.1]
    if qubit_counts is None:
        qubit_counts = [2, 3, 4]

    rows = []
    for nq in qubit_counts:
        target = "1" * nq  # all-ones target
        qc = build_grover_circuit(nq, target)
        for nt in noise_types:
            for nl in noise_levels:
                nm = get_noise_model(nl, nt)
                res = simulate_circuit(qc, nm, shots=512)
                success = res["probabilities"].get(target, 0.0)
                rows.append(
                    {
                        "Qubits": nq,
                        "Noise Type": nt,
                        "Noise Level": nl,
                        "Success Probability": success,
                    }
                )
    return pd.DataFrame(rows)


def generate_security_gauge_data() -> list[dict]:
    """
    Returns security strength data (effective bits of security against
    classical and quantum attacks) for gauge chart visualization.
    """
    return [
        {
            "Algorithm": "RSA-2048",
            "Type": "Asymmetric",
            "Classical Security (bits)": 112,
            "Quantum Security (bits)": 0,
            "Status": "❌ Broken by Shor's",
            "Color": "#ef4444",
        },
        {
            "Algorithm": "AES-128",
            "Type": "Symmetric",
            "Classical Security (bits)": 128,
            "Quantum Security (bits)": 64,
            "Status": "⚠️ Weakened by Grover's",
            "Color": "#f59e0b",
        },
        {
            "Algorithm": "AES-256",
            "Type": "Symmetric",
            "Classical Security (bits)": 256,
            "Quantum Security (bits)": 128,
            "Status": "✅ Quantum-Safe (doubled key)",
            "Color": "#22c55e",
        },
        {
            "Algorithm": "CRYSTALS-Kyber-768",
            "Type": "Lattice (KEM)",
            "Classical Security (bits)": 192,
            "Quantum Security (bits)": 192,
            "Status": "✅ NIST FIPS 203",
            "Color": "#06b6d4",
        },
        {
            "Algorithm": "CRYSTALS-Dilithium-3",
            "Type": "Lattice (Signature)",
            "Classical Security (bits)": 192,
            "Quantum Security (bits)": 192,
            "Status": "✅ NIST FIPS 204",
            "Color": "#8b5cf6",
        },
        {
            "Algorithm": "SPHINCS+-256f",
            "Type": "Hash-Based (Signature)",
            "Classical Security (bits)": 256,
            "Quantum Security (bits)": 256,
            "Status": "✅ NIST FIPS 205",
            "Color": "#ec4899",
        },
    ]
