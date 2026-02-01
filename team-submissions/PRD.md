Product Requirements Document (PRD)  
**Project Name:** Nvidia  
**Team Name:** \[@SCale\]  
**GitHub Repository:** \[https://github.com/katiejones404/2026-NVIDIA-MIT-iQuHack/tree/main\]

## **1\. Team Roles & Responsibilities** 

| **Project Lead** (Architect) | \[Jiarong Xu\] | \[@rebecca922\] | \[@handle\] |  
| **GPU Acceleration PIC** (Builder) | \[Lingjia Shi\] | \[@Siryouka\] | \[@siryouka\] |  
| **Quality Assurance PIC** (Verifier) | \[Katie Jones\] | \[@katiejones404\] | \[@katiejones444\] |  
| **Technical Marketing PIC** (Storyteller) | \[Emma Wilmott\] | \[@emmawilmott63\] | \[@emdeuk\] 

---

## **2\. The Architecture**

Owner: Jiarong Xu

**Choice of Quantum Algorithm**

* Algorithm: Quantum Imaginary Time Evolution (QITE) implemented with a variational **Matrix Product State (MPS) ansatz**, combined with **generative tensor network sampling**.  
* Motivation:   
* We adopt QITE instead of the tutorial’s Counterdiabatic (CD) method and standard VQE or Grover-based approaches for the following reasons:

* #### **Landscape Robustness**

* The LABS problem has a highly rugged energy landscape with many local minima. QITE approximates imaginary-time evolution via McLachlan’s variational principle, suppressing high-energy components of the state and biasing the evolution toward low-energy configurations. This energy-filtering behavior is often more robust on rugged landscapes than purely gradient-based variational methods (McArdle et al., 2019).  
  

* #### **Scalability via Matrix Product States**

* Imaginary-time evolution heuristically favors low-energy states with limited entanglement, making tensor-network representations suitable. Using an MPS ansatz allows us to control computational cost via the bond dimension and avoid full state-vector simulation. We leverage CUDA-Q with the cuTensorNet backend to efficiently run MPS contractions on GPU hardware.  
  

* #### **Generative Synergy with Classical Optimization**

* Rather than directly targeting the global optimum, we use QITE as a generative heuristic that concentrates probability mass on low-energy configurations. The resulting samples are used to initialize a classical Multi-Trajectory Search (MTS) for efficient local refinement. This hybrid approach combines quantum-inspired global exploration with fast classical optimization.  
  

### **Literature Review**

**Reference:** \[Variational (matrix) product states for combinatorial optimization, Preisser et. al., arXiv:2512.20613\]

* **Relevance:** This work demonstrates that variational MPS ansatz can efficiently represent and optimize large combinatorial problems such as MaxCut. It motivates our use of MPS to compress the LABS state space while retaining sufficient expressive power to find near-optimal solutions.

**Reference:** \[A quantum-inspired tensor network method for constrained combinatorial optimization problems, Hao et. al., arXiv:2203.15246\]

* **Relevance:** This paper shows that tensor-network methods can act as structured sampling engines for combinatorial optimization. This supports our use of MPS as a generative model to produce high-quality candidate solutions rather than relying on random sampling.

**Reference:** \[Combinatorial optimization with quantum imaginary time evolution, Bauer et. al., arXiv:2312.16664\]

* **Relevance:** This work introduces QITE as a cooling-based approach for discrete optimization, where imaginary-time evolution filters out high-energy configurations. It provides the conceptual basis for using QITE as a low-energy biasing and sampling strategy.

**Reference:** \[Variational ansatz-based quantum imaginary time evolution, McArdle et. al., npj Quantum Information, 2019\]

* **Relevance:** McArdle et al. establish the variational framework for implementing imaginary-time evolution using McLachlan’s principle. This forms the theoretical foundation for our QITE implementation with a parameterized ansatz.

---

## **3\. The Acceleration Strategy**

Owner: Lingjia

### **Quantum Acceleration (CUDA-Q)**

* Strategy: Complete end-to-end debugging and regression testing on a single L4 GPU. After validation, switch to the NVIDIA multi-GPU (nvidia-mgpu) backend and distribute parameter/sample parallelism across multiple L4 GPUs to scale N. When single-GPU memory becomes a bottleneck or higher mixed-precision throughput is required, migrate to 1–2 A100 GPUs for final large-scale benchmarking.

### **Classical Acceleration (MTS)**

* Strategy:Standard MTS evaluates neighbors sequentially. We will rewrite the energy function using CuPy and convert neighbor evaluation to a batched mode (evaluating K neighbors at once). In addition, we will implement critical kernels with Numba CUDA, combining multi-trajectory concurrency with streamed asynchronous memory transfers. This will significantly increase neighbors/sec and reduce CPU–GPU round-trip overhead

### **Hardware Targets**

* Dev Environment: **NVIDIA L4** (1 GPU per node, or 2 GPUs on a single machine)   
* Production Environment**: NVIDIA A100 80GB**

---

## **4\. The Verification Plan**

## Owner: Katie

In the context of the Low Autocorrelation Binary Sequence (LABS) problem and quantum-enhanced optimization, validation is critical for several specific reasons:

**1\. Verifying the Quantum-Classical Interface**

Quantum computers provide results as bitstrings of 0s and 1s, while the LABS problem is mathematically defined using spins of \+1 and \-1 Validation ensures that your conversion logic is correct. If the mapping is inverted or misaligned, your optimization algorithm will be searching an entirely different (and incorrect) energy landscape.

**2\. Ensuring Physical/Mathematical Soundness**

The LABS problem is notoriously difficult because the energy landscape is "rugged" (filled with many local minima). Validation confirms that your code respects the fundamental symmetries of the problem:

- Bit-flip Symmetry: If you flip every bit in a sequence, the energy must stay the same.  
- Reversal Symmetry: If you read the sequence backward, the energy must stay the same.

**3\. Anchoring to "Known Truths"**

Because finding the global minimum for large N is an unsolved problem in mathematics, we must anchor our code to small cases where the answer is known (like the Barker sequences). By verifying that your code correctly identifies E=2 for N=4, you gain confidence that your algorithm's findings for N=25 or N=50 are trustworthy. We have code that solves E for single-digit N, and will assert these as ground truths.

**4\. Hardware/Simulation Trust**

Quantum devices can introduce noise or errors. By cross-referencing a quantum sample against a classical energy calculation, you prove that the "best" string identified by the QPU actually corresponds to a low-energy state in the real world. This justifies using a quantum approach in the first place.

To ensure the accuracy of our optimization results, we implemented validation tests that verifies the core logic from multiple angles. We first performed a hand-calculated baseline check using the N=4 Barker sequence (\[1, 1, 1, \-1\]), confirming our energy function correctly identifies the known minimum energy of 2\. 

We then verified the mathematical symmetries of the LABS problem, confirming that our implementation is invariant under bit-flip (s to \-s) and sequence reversal. Finally, we established a quantum-classical cross-reference by passing bitstrings sampled from the CUDA-Q kernel back into our classical energy evaluator. This verification confirms that the quantum-enhanced population seeding correctly interfaces with the classical Memetic Tabu Search (MTS) workflow.

### **AI Checks**

* Framework: pytest  
* While writing our code, we are double checking with credible research sources. Furthermore, during our checking of energy values, we compare our findings to known energy values.  
* For example, a Barker sequence is a binary sequence where the peak sidelobe of its autocorrelation is minimal. For N=4, a known Barker sequence is \[1, 1, 1, \-1\], and its target energy is 2\.

---

## **5\. Execution Strategy & Success Metrics**

Owner: Emma

### **Agentic Workflow**

* Conscious prompting: We have separate IDEs (drafting in VScode, and writing directly in qBraid) and AI tabs. Rather than having code auto-generate or auto-suggest, we write prompts for specific requests.  
* Documentation: We are maintaining a shared google doc to keep track of general progress and ideas, noting where AI helped and where it failed.  
* AI “peer-review”: We are using an agentic combination method to try to lower the probability of one single model perpetuating its own hallucinations. Our workflow environment includes ChatGPT, Claude, and Gemini. For short conversations, we give the same prompt to each agent and confirm that the responses agree. For longer conversations, we summarize the prompt and response from 1 model, then prompt the other 2 models to analyze the conversation and assess its accuracy. If one agent suggests, for example, an outline, then we check that it makes sense and then ask a different agent for help on working through the details of implementation.   
* Human peer-review: We are talking through general logic, sanity-checking intermediate results, and reviewing final versions of code together to look for obvious errors.  
* Testing: The QA Lead will run specific tests to combat AI hallucinations.

### **Success Metrics**

Minimum goal: match Tutorial baseline performance

* Successfully run simulation for N=7 (this is the maximum we ran on the Tutorial baseline, so this is a good minimum goal and comparison benchmark for other metrics)  
  * Pass validation suite

Target goals

* Accuracy: Energy within 20% of classical value  
* Scale: Successfully run simulation (pass tests) for N=37 (highest value in original paper)  
* Speedup: 4x speedup over CPU-only Tutorial Baseline 

## **Visualization Plan**

### **Plot 1 — Time-to-Solution vs. Problem Size**

**Description:**

* X-axis: Problem size (N)  
* Y-axis: Time-to-solution (log scale)  
* Curves:  
  * CPU baseline  
  * GPU (L4)  
  * GPU (A100)

### **Plot 2 — Convergence Rate Comparison**

**Description:**

* X-axis: Iteration count  
* Y-axis: Energy / Objective value  
* Curves:  
  * Quantum-informed seed (CUDA-Q assisted)  
  * Random initialization (classical baseline)

## **Optional Stretch Metrics (If Time Allows)**

* **Cost Efficiency**  
  * Cost per successful run (CPU vs L4 vs A100)  
* **Scaling Efficiency**  
  * Speedup vs number of GPUs (parameter-parallel regime)

---

## **6\. Resource Management Plan**

Owner: Lingjia

* Plan: We follow a strict CPU → L4 → A100 escalation policy. All development and debugging happens on CPU or cheap L4 GPUs. Expensive A100 instances are only used for time-boxed final benchmarks, under direct supervision of the GPU Acceleration PIC, with both automated and manual shutdown safeguards to prevent idle burn.


  
