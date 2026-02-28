import math
import numpy as np

def classical_factorization_scaling(n_bits_range: list) -> list:
    """
    Estimates the runtime scaling of classical factorization.
    Uses the General Number Field Sieve (GNFS) complexity approximation:
    L_n[1/3, c] = exp(c * (ln n)^(1/3) * (ln ln n)^(2/3))
    
    We simplify and return an arbitrary scale representing complexity (not exact seconds)
    for plotting purposes.
    """
    scaling_values = []
    c = 1.9  # Constant for GNFS
    
    for bits in n_bits_range:
        # Avoid math domain error by setting lower bounds for bits
        if bits < 4:
            bits = 4
            
        n = 2**bits
        # Complexity formula approximation
        ln_n = math.log(n)
        ln_ln_n = math.log(ln_n)
        
        complexity = math.exp((c * (ln_n ** (1/3)) * (ln_ln_n ** (2/3))))
        scaling_values.append(complexity)
        
    return scaling_values


def shor_scaling(n_bits_range: list) -> list:
    """
    Estimates the runtime scaling of Shor's algorithm.
    Shor's scales polynomially: O((log N)^3) = O(bits^3).
    Returns an arbitrary scale representing operations complexity.
    """
    scaling_values = []
    for bits in n_bits_range:
        # O(b^3) complexity approximation
        complexity = bits ** 3
        scaling_values.append(complexity)
        
    return scaling_values


def classical_search_scaling(n_bits_range: list) -> list:
    """
    Estimates worst-case/average-case brute force search scaling for symmetric keys.
    O(N) where N = 2^bits.
    """
    scaling_values = []
    for bits in n_bits_range:
        scaling_values.append(2 ** bits)
    return scaling_values


def grover_scaling(n_bits_range: list) -> list:
    """
    Estimates Grover's algorithm runtime scaling.
    O(sqrt(N)) where N = 2^bits.
    """
    scaling_values = []
    for bits in n_bits_range:
        scaling_values.append(math.isqrt(2 ** bits))
    return scaling_values
