import math
import time
import random

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def generate_keypair(p, q):
    """
    Generates a simple RSA keypair given two primes.
    """
    if not (is_prime(p) and is_prime(q)):
        raise ValueError("Both numbers must be prime.")
    elif p == q:
        raise ValueError("p and q cannot be equal")

    n = p * q
    phi = (p - 1) * (q - 1)

    # Choose an integer e such that e and phi(n) are coprime
    e = random.randrange(1, phi)
    g = gcd(e, phi)
    while g != 1:
        e = random.randrange(1, phi)
        g = gcd(e, phi)

    # Use Extended Euclid's Algorithm to generate the private key
    d = pow(e, -1, phi)

    # Return public and private keypair
    # Public key is (e, n) and private key is (d, n)
    return ((e, n), (d, n))

def classical_factorization(n):
    """
    Simulates classical brute force factorization (trial division).
    Returns the prime factors (p, q), execution time, and number of iterations.
    """
    start_time = time.time()
    iterations = 0

    if n % 2 == 0:
        return 2, n // 2, time.time() - start_time, 1

    factor = 3
    while factor * factor <= n:
        iterations += 1
        if n % factor == 0:
            exec_time = time.time() - start_time
            return factor, n // factor, exec_time, iterations
        factor += 2

    # n is prime
    exec_time = time.time() - start_time
    return n, 1, exec_time, iterations
