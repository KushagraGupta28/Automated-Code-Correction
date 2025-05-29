# Automated Code Correction using Multi-Agent LLM System

This project presents a fully automated, interpretable code repair system using Large Language Models (LLMs). It is built around a **six-agent pipeline** that mimics a structured, human-like debugging process. The system leverages the [QuixBugs dataset](https://github.com/google-research-datasets/QuixBugs) to test and repair buggy Python programs and is powered by **Gemini 2.0 Flash** for all LLM-based tasks.

## 📌 Overview

The system is designed to:
- Understand the intended functionality of code.
- Locate and classify bugs.
- Generate targeted fixes.
- Create and run test cases to verify repairs.
- Iteratively refine fixes when validation fails.

## 🧠 Multi-Agent Pipeline

All agents operate sequentially and are orchestrated in a single unified file: **`pipeline.py`**.

### Agent Descriptions:
1. **Agent 1 – Purpose Extractor**
   - Extracts a natural language description of the code's intended behavior.

2. **Agent 2 – Bug Reporter**
   - Locates the bug in the code and explains the issue using the code and its extracted purpose.

3. **Agent 3 – Bug Classifier**
   - Categorizes the bug into one of 14 known bug types.

4. **Agent 4 – Code Fixer**
   - Applies a minimal and precise fix to the bug using prior context.

5. **Agent 5 – Test Case Generator**
   - Creates generalized test cases from the code's purpose and stores them in `testcases.json`.

6. **Agent 6 – Verifier**
   - Runs the generated test cases on the fixed code.
   - If any test fails, the fixed code is sent back to Agent 4 for refinement.

## 🔁 Repair Loop

- All agents are invoked **from within `pipeline.py`**, which manages the entire debugging loop.
- Failed fixes are automatically routed back for further repair using insights from previous steps.
- Logs for extracted purpose, bug report, classification, and all attempts are stored in `bug_history.json` for traceability.

## ⚙️ Architecture Highlights

- Few-shot prompting enhances the consistency and quality of responses across all agents.
- Prompts are dynamically constructed using the identified bug type and code.
- Agents reason via chain-of-thought, supporting better decision-making.
- Buggy programs are first preprocessed (e.g., line-numbered) for better interpretability.
