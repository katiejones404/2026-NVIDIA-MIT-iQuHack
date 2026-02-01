# tasks.py
import cudaq
from cudaq import spin
import unittest
import numpy as np
import time

# --- ISING MODEL LOGIC ---

def get_labs_hamiltonian(n_qubits):
    hamiltonian = 0.0
    for k in range(1, n_qubits):
        term_k = 0.0
        for i in range(n_qubits - k):
            term_k += spin.z(i) * spin.z(i + k)
        hamiltonian += term_k * term_k
    return hamiltonian

def verify_energy_with_quantum_cpu(bitstring_01):
    n = len(bitstring_01)
    ham = get_labs_hamiltonian(n)
    
    @cudaq.kernel
    def prepare_state(bits: list[int]):
        qubits = cudaq.qvector(len(bits))
        for i, b in enumerate(bits):
            if b == 1: x(qubits[i])

    # Smart Target Selection
    targets = [t.name for t in cudaq.get_targets()]
    if "qpp-cpu" in targets:
        try: cudaq.set_target("qpp-cpu")
        except: pass
    
    result = cudaq.observe(prepare_state, ham, bitstring_01)
    return int(round(result.expectation()))

# --- DETAILED TEST RUNNER ---

def run_notebook_tests(labs_energy_pm1, pm1_to_bits01, tabu_search_pm1):
    
    class DetailedTestLABS(unittest.TestCase):
        def test_energy_match(self):
            """Verify: Notebook Math == Quantum Ising Physics"""
            N_test = 8
            seq = np.random.choice([-1, 1], size=N_test)
            
            print(f"\n[STEP 1] Testing Energy Alignment (N={N_test})")
            print(f"  > Input Sequence: {seq}")
            
            e_classical = labs_energy_pm1(seq)
            bits = pm1_to_bits01(seq).tolist()
            e_quantum = verify_energy_with_quantum_cpu(bits)
            
            print(f"  > Notebook Energy Result: {e_classical}")
            print(f"  > Quantum Ising Benchmark: {e_quantum}")
            
            self.assertEqual(e_classical, e_quantum, "Energy mismatch between systems!")
            print("  > STATUS: Math Alignment Verified")

        def test_optimization(self):
            """Verify: Tabu Search effectively reduces energy"""
            N_test = 10
            s0 = np.random.choice([-1, 1], size=N_test)
            e0 = labs_energy_pm1(s0)
            
            print(f"\n[STEP 2] Testing Optimization Logic (N={N_test})")
            print(f"  > Initial Random Energy: {e0}")
            
            start_time = time.time()
            best_s, e_final = tabu_search_pm1(s0, max_iters=100)
            duration = time.time() - start_time
            
            improvement = e0 - e_final
            print(f"  > Optimized Energy:      {e_final}")
            print(f"  > Total Reduction:       {improvement}")
            print(f"  > Search Time:           {duration:.4f}s")
            
            self.assertLessEqual(e_final, e0)
            if improvement > 0:
                print("  > STATUS: Optimization Successful")
            else:
                print("  > STATUS: Search Complete (Local Minimum Found)")

    # This makes the output much cleaner in the notebook
    print("\n" + "="*50)
    print("NVIDIA iQuHACK 2026: LABS VALIDATION SUITE")
    print("="*50)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(DetailedTestLABS)
    unittest.TextTestRunner(verbosity=1, stream=None).run(suite)