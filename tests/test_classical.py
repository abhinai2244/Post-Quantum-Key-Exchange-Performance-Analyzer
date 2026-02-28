import pytest
from src.classical.rsa import is_prime, generate_keypair, classical_factorization
from src.classical.symmetric import classical_symmetric_search

def test_is_prime():
    assert is_prime(2) == True
    assert is_prime(4) == False
    assert is_prime(17) == True
    assert is_prime(15) == False

def test_generate_keypair():
    p, q = 61, 53
    public, private = generate_keypair(p, q)
    # Check if N is correct
    assert public[1] == p * q
    assert private[1] == p * q

def test_classical_factorization():
    n = 15
    factor1, factor2, _, _ = classical_factorization(n)
    assert factor1 * factor2 == n
    assert {factor1, factor2} == {3, 5}

def test_symmetric_search():
    target = 5
    key_size_bits = 3 # 0 to 7
    found_target, _, iterations = classical_symmetric_search(target, key_size_bits)
    assert found_target == 5
    assert iterations == 6 # i=0,1,2,3,4,5
