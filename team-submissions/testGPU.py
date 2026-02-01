# testGPU.py
'''in gpu-update2.ipynb put:
import testGPU
import importlib
importlib.reload(testGPU)

# Pass the functions from the notebook into the test suite
testGPU1.run_gpu_comparison_tests(
    labs_energy_pm1=labs_energy_pm1, 
    pm1_to_bits01=pm1_to_bits01, 
    tabu_search_pm1=tabu_search_pm1,
    mts_quant1=mts_quant1
)

#This will be added after we successfully find and run data
'''

# testGPU.py
import cudaq
from cudaq import spin
import numpy as np
import unittest
import time

# ---------------------------------------------------------------------
# This builds the ground-truth energy model using CUDA-Q.
# ---------------------------------------------------------------------

def get_verification_hamiltonian(N: int):
    """
    Constructs the LABS Hamiltonian by squaring the correlation terms.
    This provides a physical benchmark to test against classical math.
    """
    hamiltonian = None
    for k in range(1, N):
        term_k = None
        for i in range(N - k):
            zz = spin.z(i) * spin.z(i + k)
            term_k = zz if term_k is None else term_k + zz
        
        # The energy is the sum of squared correlations for each lag k
        term_sq = term_k * term_k
        hamiltonian = term_sq if hamiltonian is None else hamiltonian + term_sq
    return hamiltonian

def quantum_energy_verify(bitstring_01):
    """
    Runs a quantum simulation to measure the energy of a specific state.
    """
    N = len(bitstring_01)
    ham = get_verification_hamiltonian(N)
    
    @cudaq.kernel
    def state_prep(bits: list[int]):
        q = cudaq.qvector(len(bits))
        for i, b in enumerate(bits):
            if b == 1:
                x(q[i])

    # Select the high-performance target if available
    available = [t.name for t in cudaq.get_targets()]
    if "tensornet" in available:
        cudaq.set_target("tensornet")
    elif "nvidia" in available:
        cudaq.set_target("nvidia")
    
    result = cudaq.observe(state_prep, ham, bitstring_01)
    return int(round(result.expectation()))

# ---------------------------------------------------------------------
# SECTION 2: DETAILED VALIDATION SUITE
# ---------------------------------------------------------------------

def run_gpu_comparison_tests(labs_energy_pm1, pm1_to_bits01, tabu_search_pm1, mts_quant1):
    """
    Executes comparison tests to ensure the GPU notebook logic is sound.
    """

    class TestGPULABS(unittest.TestCase):
        
        def test_math_physics_alignment(self):
            """
            Ensures the classical energy function matches the quantum benchmark.
            """
            print("\n[CHECK] Verifying Energy Math vs. Quantum Physics...")
            N_test = 10
            # Create a random sequence
            seq = np.random.choice([-1, 1], size=N_test).astype(np.int8)
            
            # Classical calculation
            e_class = labs_energy_pm1(seq)
            
            # Quantum calculation
            bits = pm1_to_bits01(seq).tolist()
            e_quant = quantum_energy_verify(bits)
            
            print(f"  Sequence: {seq}")
            print(f"  Notebook Energy: {e_class}")
            print(f"  Quantum Verify:  {e_quant}")
            
            self.assertEqual(e_class, e_quant, "Classical and Quantum energies must match!")
            print("  Status: Math Alignment Verified")

        def test_hybrid_search_results(self):
            """
            Verifies that the hybrid MTS algorithm returns a valid best state.
            """
            print("\n[CHECK] Verifying Hybrid MTS Optimizer Output...")
            N_test = 12
            
            start = time.time()
            # Run a small version of the hybrid search
            res = mts_quant1(N=N_test, mts_iters=50, pop_size=10, tabu_iters=50)
            duration = time.time() - start
            
            best_e = res["best_E"]
            best_s_01 = res["best_s_01"]
            
            # Cross-check the best energy found with the quantum benchmark
            e_verify = quantum_energy_verify(best_s_01.tolist())
            
            print(f"  Best Energy Found: {best_e}")
            print(f"  Quantum Validation: {e_verify}")
            print(f"  Search Duration:    {duration:.3f}s")
            
            self.assertEqual(best_e, e_verify, "Reported best energy does not match reality!")
            print("  Status: Hybrid Results Validated")

    # Runner configuration
    print("\n" + "="*60)
    print("      NVIDIA iQuHACK 2026: UPDATED GPU VALIDATION")
    print("="*60)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGPULABS)
    unittest.TextTestRunner(verbosity=1).run(suite)