import subprocess
import tempfile
import json
import os
from typing import Dict
import textwrap

HISTORY_FILE = "bug_history.json"

# Load bug history
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        bug_history = json.load(f)
else:
    bug_history = {}

# Save updated bug history
def save_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump(bug_history, f, indent=2)

def run_test_case_with_input(code_path: str, test_input: str) -> str:
    try:
        result = subprocess.run(
            ['python', code_path],
            input=test_input.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        return result.stdout.decode().strip()
    except subprocess.TimeoutExpired:
        return "Timeout"
    except Exception as e:
        return f"Error: {str(e)}"

import re

def run_tests_with_pytest(file_name: str, fixed_code: str, test_case_file: str) -> Dict:
    # Extract the first function name from the fixed code
    match = re.search(r'def\s+([a-zA-Z_]\w*)\s*\(', fixed_code)
    if not match:
        raise ValueError("No function definition found in fixed code.")
    function_name = match.group(1)

    # Wrapper to call main function with stdin input
    function_call_wrapper = textwrap.dedent(f"""
    if __name__ == '__main__':
        import sys
        input_data = sys.stdin.read().strip()
        print({function_name}(int(input_data)))
    """)


    # Write fixed code + wrapper to a temporary file
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as temp_code_file:
        temp_code_file.write(fixed_code + function_call_wrapper)
        temp_code_path = temp_code_file.name

    # Load test cases
    with open(test_case_file, "r") as f:
        test_cases_data = json.load(f)

    test_cases = [tc for tc in test_cases_data if tc['file_name'] == file_name]
    failed_cases = []

    for case in test_cases:
        inputs = case['inputs']
        expected_outputs = case['outputs']
        for i, test_input in enumerate(inputs):
            expected_output = str(expected_outputs[i]).strip()
            actual_output = run_test_case_with_input(temp_code_path, str(test_input).strip())
            if actual_output != expected_output:
                failed_cases.append({
                    "input": test_input,
                    "expected": expected_output,
                    "actual": actual_output
                })

    os.remove(temp_code_path)

    passed = len(failed_cases) == 0
    test_result = {
        "status": "passed" if passed else "failed",
        "failed_cases": failed_cases
    }

    # Save failed cases to bug history
    if not passed:
        if file_name not in bug_history:
            bug_history[file_name] = {}
        bug_history[file_name]["failed_test_cases"] = failed_cases
        save_history()

    return test_result
