from agent_2 import detect_code_bug
from agent_3 import detect_code_bug_type
from agent_4 import fixed_code
from agent_1 import detect_code_purpose
from agent_5 import generate_test_cases_from_buggy
from agent_6 import run_tests_with_pytest
from agent_6_substitute import test_code_llm
import json
import os

# === Shared Bug History File ===
HISTORY_FILE = "bug_history.json"

# Load history if exists
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        bug_history = json.load(f)
else:
    bug_history = {}

# Save updated history
def save_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump(bug_history, f, indent=2)

def main():
    #ENTER THE PYHTON_PROGRAMS FOLDER FOR ALL FILES TO BE EXECUTED AT ONCE
    file_name = "C:/Users/mitaksh/OneDrive/Desktop/RESEARCH INTERN/Code-Refactoring-QuixBugs/python_programs/quicksort.py"
    
    # Load the original buggy code
    with open(file_name, "r") as f:
        buggy_code = f.read()
    if file_name not in bug_history:
        bug_history[file_name] = {}
    code,agent_1_output = detect_code_purpose(file_name)
    bug_history[file_name]["purpose"] = agent_1_output
    bug_history[file_name]["code"] = code
    save_history()


    
    agent_2_output = detect_code_bug(file_name, buggy_code)
    bug_history[file_name] = {
        **bug_history.get(file_name, {}),
        "bug_report": agent_1_output,
    }
    save_history()

    # Step 2: Agent 2
    bug_type, reasoning = detect_code_bug_type(file_name, buggy_code, agent_1_output)
    bug_history[file_name].update({
        "bug_type": bug_type,
        "bug_type_reasoning": reasoning
    })
    save_history()

    
    
    
    test_file_path = generate_test_cases_from_buggy(file_name, buggy_code, agent_1_output)
    test_file_path = 'testcases.json'
    save_history()

    
    max_attempts = 3
    attempt = 0
    

    while attempt < max_attempts:
        print(f"\n--- Attempt {attempt + 1} ---")

        # Step 1: Fix the code
        agent_3_output = fixed_code(file_name,buggy_code)
        bug_history[file_name][f"fixed_code_attempt_{attempt + 1}"] = agent_3_output

        # Step 2: Test the fixed code
        passed, detail = test_code_llm(file_name, agent_3_output, "testcases.json")

        if passed:
            print(" All test cases passed.")
            bug_history[file_name]["fixed_code"] = agent_3_output
            bug_history[file_name].pop("failed_test_cases", None)  # Clear old failures

            # === Save to fixed folder ===
            fixed_folder = "C:/Users/mitaksh/OneDrive/Desktop/RESEARCH INTERN/Code-Refactoring-QuixBugs/fixed_programs"
            os.makedirs(fixed_folder, exist_ok=True)

            original_filename = os.path.basename(file_name)  # e.g., "bitcount.py"
            fixed_path = os.path.join(fixed_folder, original_filename)

            with open(fixed_path, "w") as f:
                f.write(agent_3_output)

            print(f"💾 Fixed code saved to: {fixed_path}")
            break

        else:
            print("Some test cases failed:", detail)
            bug_history[file_name]["failed_test_cases"] = detail

        save_history()
        attempt += 1
    # === Save to fixed folder ===
    fixed_folder = "C:/Users/mitaksh/OneDrive/Desktop/RESEARCH INTERN/Code-Refactoring-QuixBugs/fixed_programs"
    os.makedirs(fixed_folder, exist_ok=True)

    original_filename = os.path.basename(file_name)  # e.g., "bitcount.py"
    fixed_path = os.path.join(fixed_folder, original_filename)

    with open(fixed_path, "w") as f:
        f.write(agent_3_output)

    print(f" Fixed code saved to: {fixed_path}")
    
      
if __name__ == "__main__":
    main()
