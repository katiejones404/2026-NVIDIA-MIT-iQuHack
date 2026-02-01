# Workflow

AI Agents: ChatGPT, Gemini, Claude

**AI-Peer-Review**

* Confidence by (lack of) contradiction – comparing answers from different agents to try to catch glaring errors or inconsistent logic  
* Frequent switch – switching between agents after every step to try to prevent compounding errors by an incorrect train of AI “thought”  
* Self-evaluation – asking AI agents to review conversations and outputs from other AI agents 

**Manual-Peer-Review**

* Reading through code to ensure consistent naming, counting, logic, etc.  
* For names of algorithms, strategies, packages, or formulas – verification through cross-referencing publishable, trustable sources by human authors.

# Verification Strategy

Framework: unittest, cudaq

We built a Quantum Ising model-based unit test to rigorously verify physical accuracy of our energy results. The script takes a bitstring, builds a quantum circuit to represent that string, and uses cudaq.observe to calculate the expectation value of the Ising Hamiltonian. This gives the simulated physical energy, or “quantum truth.”

# Vibe Log

| Wins | Gemini quickly matched our intended algorithms and steps to Cuda-Q packages/kernels. Claude and Gemini were surprisingly helpful at pointing us to real research papers involving QITE, ITE, MPS, and Tensor Networks. |
| :---- | :---- |
| Fails | While discussing strategy with ChatGPT, we switched from full names of algorithms to acronyms and abbreviations. It ended up describing and giving us code to implement Multi-Trajectory Search (MTS) instead of Mimetic-Tabu Search (MTS), and didn’t clarify or seem to notice the difference.  ChatGPT liked to make up colloquialisms or coin terms without explaining that it was making up something new. We couldn’t find any papers about “Quantum Superposition Bias” because it didn’t exist. When we asked Gemini to explain QBS, it started explaining something slightly different … that also didn’t quite exist.  |
| Learns | AI makes assumptions and runs with them. We learned to avoid being vague or using acronyms (such as MTS), and always be explicit and detailed. AI will repeat information (including mistakes) the longer you stay in the same conversation. We learned to frequently start new conversations, give background only on the individual code section we were working on, and then ask for a short, simple, specific task. This worked better for us than trying to overload it with all of the information about our plan, current code, and corrected mistakes. |

