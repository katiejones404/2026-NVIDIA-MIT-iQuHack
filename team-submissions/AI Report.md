# **AI Workflow**

## **AI Agents**

* **ChatGPT**  
* **Gemini**  
* **Claude**

Each agent is used based on its strengths, and we frequently switch between them during different stages of the workflow.

## **Workflow Overview**

### **1\. Understanding the problem (ChatGPT)**

* We start by using ChatGPT to help us understand the overall challenge.  
* We ask ChatGPT to explain unfamiliar terms and techniques in simple language.  
* Our prompts usually request:  
  * an intuitive explanation first,  
  * followed by a more detailed and technical explanation,  
  * with all relevant terms clearly defined.  
* We continue interacting with ChatGPT through follow-up questions until we reach a solid understanding of the topic.

### **2\. Task breakdown and planning (ChatGPT)**

* After understanding the topic, we ask ChatGPT to break the work into smaller, manageable tasks.  
* We use this to form a step-by-step action plan for the project.  
* Each task is treated independently to avoid confusion and error accumulation.

### **3\. Implementation and drafting (Gemini)**

* We then move to Gemini to help us write code based on the defined requirements.  
* After Gemini generates the code, we stay in the same chat to:  
  * ask Gemini to explain what the code does,  
  * conduct an AI peer review of the logic and structure.  
* In some cases, we take the opposite approach:  
  * we provide draft code or draft text,  
  * and ask Gemini to check grammar, improve clarity, or polish the content.

### **4\. Prompting approach (used throughout)**

* While interacting with AI, we try to provide prompts that are as specific as possible.  
* We usually specify:  
  1. the task scope,  
  2. the expected format,  
  3. the style or level of detail.  
* We intentionally use AI for **one task at a time**, rather than combining multiple objectives in a single prompt.  
* When asking AI to read a paper, for example, we clearly define steps such as:  
  1. Giving an overview focusing on the main contribution.  
  2. Explaining the method and implementation.  
  3. Summarizing the results and key findings.

## **AI Peer Review**

* **Cross-agent comparison:**  
  We compare answers from different AI agents to identify contradictions or inconsistent logic.  
* **Frequent switching:**  
  We switch between agents after each major step to reduce the risk of compounding errors from a single AI’s reasoning path.  
* **Self-evaluation:**  
  We ask AI agents to review outputs or conversations produced by other AI agents.

## **Manual Peer Review**

* We manually read through code to check naming consistency, logic flow, indexing, and counting.  
* For algorithm names, strategies, packages, or formulas, we verify correctness by cross-referencing reliable, publishable sources written by human authors.

# Verification Strategy

Framework: unittest, cudaq

We built a Quantum Ising model-based unit test to rigorously verify physical accuracy of our energy results. The script takes a bitstring, builds a quantum circuit to represent that string, and uses cudaq.observe to calculate the expectation value of the Ising Hamiltonian. This gives the simulated physical energy, or “quantum truth.”

# Vibe Log

| :---- | :---- |
| Wins | Gemini quickly matched our intended algorithms and steps to Cuda-Q packages/kernels. Claude and Gemini were surprisingly helpful at pointing us to real research papers involving QITE, ITE, MPS, and Tensor Networks. |
| Fails | While discussing strategy with ChatGPT, we switched from full names of algorithms to acronyms and abbreviations. It ended up describing and giving us code to implement Multi-Trajectory Search (MTS) instead of Mimetic-Tabu Search (MTS), and didn’t clarify or seem to notice the difference.  ChatGPT liked to make up colloquialisms or coin terms without explaining that it was making up something new. We couldn’t find any papers about “Quantum Superposition Bias” because it didn’t exist. When we asked Gemini to explain QBS, it started explaining something slightly different … that also didn’t quite exist.  |
| Learns | AI works best when tasks are broken down into smaller parts. It’s more effective to ask AI to focus on one thing at a time, such as brainstorming first, discussing each idea individually, and then asking how to implement them separately. AI also performs better when given clear, step-by-step instructions, similar to following an SOP. AI makes assumptions and runs with them. We learned to avoid being vague or using acronyms (such as MTS), and always be explicit and detailed. AI will repeat information (including mistakes) the longer you stay in the same conversation. We learned to frequently start new conversations, give background only on the individual code section we were working on, and then ask for a short, simple, specific task. This worked better for us than trying to overload it with all of the information about our plan, current code, and corrected mistakes. |

