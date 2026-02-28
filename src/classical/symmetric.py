import time
import random

def classical_symmetric_search(target, key_size_bits):
    """
    Simulates a classical brute force search for a symmetric key (like AES, but toy sizes).
    Returns the target, time taken, and iterations required.
    """
    search_space = 2 ** key_size_bits
    if target >= search_space:
        raise ValueError("Target is outside the search space.")

    start_time = time.time()
    iterations = 0

    # In worst case brute force we check all. On average we check N/2.
    # To simulate an actual randomized brute-force attempt up to hitting the target:
    for i in range(search_space):
        iterations += 1
        if i == target:
            exec_time = time.time() - start_time
            return target, exec_time, iterations

    exec_time = time.time() - start_time
    return -1, exec_time, iterations
