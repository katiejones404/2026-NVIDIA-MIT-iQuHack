# testGPU.py
'''in gpu-update2.ipynb put:
import testGPU1
import importlib
importlib.reload(testGPU1) # Ensures code changes are picked up

# Pass the functions defined in the notebook into the tester
testGPU1.run_gpu_comparison_tests(
    labs_energy_fn=labs_energy_pm1, 
    optimizer_fn=tabu_search_pm1, 
    bits_converter_fn=pm1_to_bits01
)

#This will be added after we successfully find and run data
'''
import cudaq
from cudaq import spin
import numpy as np
import unittest
import time

# ---------------------------------------------------------------------
# SECTION 1: QUANTUM PHYSICS VALIDATION LOGIC
# This section uses CUDA-Q to build a Hamiltonian that represents
# the Low Autocorrelation Binary Sequence (LABS) problem.
# ---------------------------------------------------------------------

def get_labs_hamiltonian(n_qubits):
    """
    Creates a Spin Hamiltonian where the ground state (lowest energy)
    corresponds to the optimal LABS sequence.
    """
    hamiltonian = 0.0
    # The LABS energy is the sum of the squares of correlations at each lag 'k'
    for k in range(1, n_qubits):
        correlation_k = 0.0
        for i in range(n_qubits - k):
            # spin.z(i) represents the value (+1 or -1) of the i-th bit
            correlation_k += spin.z(i) * spin.z(i + k)
        
        # We square the  correlation operator to match the LABS objective function
        hamiltonian += correlation_k * correlation_k
    return hamiltonian

def quantum_energy_benchmark(bitstring):
    """
    Calculates the energy of a specific bitstring using a Quantum Simulator.
    This serves as our 'Source of Truth'.
    """
    n = len(bitstring)
    ham = get_labs_hamiltonian(n)
    
    # Define a simple kernel to prepare the state corresponding to the bitstring
    @cudaq.kernel
    def prepare_state(bits: list[int]):
        qreg = cudaq.qvector(len(bits))
        for i, val in enumerate(bits):
            if val == 1:
                x(qreg[i]) # Flip to state |1> if the bit is 1

    # Use the 'nvidia' GPU backend if available, otherwise fallback to 'qpp' (should not need)
    targets = [t.name for t in cudaq.get_targets()]
    selected_target = "nvidia" if "nvidia" in targets else "qpp"
    cudaq.set_target(selected_target)

    # Observe calculates the expectation value <Psi|H|Psi>
    # For a classical bitstring state, this is  the Ising energy.
    result = cudaq.observe(prepare_state, ham, bitstring)
    return int(round(result.expectation()))

# ---------------------------------------------------------------------
# SECTION 2: COMPARISON TEST SUITE
# ---------------------------------------------------------------------

def run_gpu_comparison_tests(labs_energy_fn, optimizer_fn, bits_converter_fn):
    """
    A test suite that compares classical results with 
    quantum-simulated reality.
    """

    class TestGPULABS(unittest.TestCase):
        
        def test_energy_consistency(self):
            """
            Verification: Does the classical math match the Quantum Hamiltonian?
            This ensures the logic in the notebook is physically accurate.
            """
            print("\n[TEST] Verifying Classical vs. Quantum Energy Consistency...")
            test_n = 8
            # Generate a random sequence of +1 and -1
            sequence = np.random.choice([-1, 1], size=test_n)
            
            # Calculate energy using the notebook function
            classical_energy = labs_energy_fn(sequence)
            
            # Convert sequence to 0/1 bits and calculate using CUDA-Q Hamiltonian
            bits = bits_converter_fn(sequence).tolist()
            quantum_energy = quantum_energy_benchmark(bits)
            
            print(f"  Sequence: {sequence}")
            print(f"  Classical Math Result: {classical_energy}")
            print(f"  Quantum Ising Result:   {quantum_energy}")
            
            self.assertEqual(classical_energy, quantum_energy, 
                             "Warning, Classical energy calculation deviates from Quantum physics!")
            print("  Result: SUCCESS (Math is consistent with physics)")

        def test_optimization_validity(self):
            """
            Verification: Does the optimizer find a 'better' state?
            Ensures the minimized energy is lower than the starting point.
            """
            print("\n[TEST] Verifying Optimizer Energy Minimization...")
            test_n = 12
            initial_seq = np.random.choice([-1, 1], size=test_n)
            e_start = labs_energy_fn(initial_seq)
            
            start_time = time.time()
            # Run the MTS/Tabu optimizer from the notebook
            best_seq, e_final = optimizer_fn(initial_seq, max_iters=50)
            end_time = time.time()
            
            print(f"  Initial Energy: {e_start}")
            print(f"  Minimized Energy: {e_final}")
            print(f"  Execution Time: {end_time - start_time:.4f}s")
            
            self.assertLessEqual(e_final, e_start, "Optimizer failed to find a lower or equal energy state.")
            
            # Final sanity check: Verify the final state with the Quantum benchmark
            final_bits = bits_converter_fn(best_seq).tolist()
            e_verify = quantum_energy_benchmark(final_bits)
            self.assertEqual(e_final, e_verify, "Optimized state energy is inconsistent when cross-checked.")
            
            print("  Result: SUCCESS (Optimizer reduced energy correctly)")

    # Launch the tests
    print("="*60)
    print("      NVIDIA iQuHACK 2026: GPU VALIDATION STARTING")
    print("="*60)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGPULABS)
    unittest.TextTestRunner(verbosity=1).run(suite)