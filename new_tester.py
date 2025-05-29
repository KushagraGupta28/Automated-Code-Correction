import copy
import json
import types
import os
import pytest # type: ignore

def py_try_fixed(algo, *args):
    """Run the fixed version of the given algorithm with provided arguments."""
    module = __import__("fixed_programs." + algo)
    fx = getattr(module, algo)
    return getattr(fx, algo)(*args)

def get_all_fixed_programs():
    """List all Python files in the fixed_programs directory (excluding __init__.py)."""
    folder_path = "fixed_programs"
    return [f[:-3] for f in os.listdir(folder_path)
            if f.endswith(".py") and f != "__init__.py"]

# Collect all test cases dynamically
test_cases = []

for algo in get_all_fixed_programs():
    try:
        with open(f"json_testcases/{algo}.json", 'r') as f:
            for line in f:
                py_testcase = json.loads(line)
                test_in, expected_out = py_testcase
                if not isinstance(test_in, list):
                    test_in = [test_in]
                test_cases.append((algo, test_in, expected_out))
    except FileNotFoundError:
        print(f"Warning: Testcase file missing for {algo}")

@pytest.mark.parametrize("algo,test_input,expected_output", test_cases)
def test_fixed_program(algo, test_input, expected_output):
    output = py_try_fixed(algo, *copy.deepcopy(test_input))
    assert output == expected_output, f"{algo} failed for input {test_input}. Expected {expected_output}, got {output}"
