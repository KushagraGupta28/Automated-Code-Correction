import os
import json
import re
import google.generativeai as genai  # type: ignore
from agent_4 import detect_code_purpose

genai.configure(api_key="#YOUR API KEY HERE")

SYSTEM_INSTRUCTION = """
You are a skilled code assistant focused on generating test cases.

Your input:
1. The buggy Python code snippet (may contain bugs).
2. A clear description of the code’s intended purpose or functionality.

Your task:
- Analyze the buggy code and the purpose description.
- Understand the inputs and outputs expected from the program.
- Generate valid and realistic input-output test cases that correspond to the intended functionality.
- Avoid bias from bugs; create test cases based on the code’s stated purpose, not on the fixed code.
- Ensure test cases fit the code’s input/output structure and data types.
- Output ONLY a JSON array of test cases, each with “input” and “expected_output”.
Generate only 5 test cases.

Format example:

[
  {
    "input": [input1, input2, ...],
    "expected_output": output_value
  },
  ...
]
"""

generation_config = {
    'temperature': 0.7,
    'top_p': 0.95,
    "top_k": 40,
    "max_output_tokens": 200,
    "response_mime_type": "text/plain"
}

agent_1 = genai.GenerativeModel(
    model_name='gemini-2.0-flash-exp',
    generation_config=generation_config,
    system_instruction=SYSTEM_INSTRUCTION
)

chat_session = agent_1.start_chat()

def add_line_numbers(code: str) -> str:
    return '\n'.join([f"{i+1}. {line}" for i, line in enumerate(code.splitlines())])

def generate_test_cases_from_buggy(file_name: str, buggy_code: str, code_purpose: str) -> str:
    numbered_code = add_line_numbers(buggy_code)

    prompt = f"""
    Buggy code:
    \"\"\" 
    {numbered_code}
    \"\"\" 

    Purpose of the code:
    \"\"\" 
    {code_purpose}
    \"\"\" 

    Generate a set of valid input-output test cases based on the intended purpose and code structure.
    Output ONLY the test cases as a JSON array in the format:
    [
      {{
        "input": [...],
        "expected_output": ...
      }},
      ...
    ]
    Generate only 5 test cases.
    """

    response = chat_session.send_message(prompt)
    
    
    # Try to parse the JSON from the LLM response
    try:
        raw_test_cases = json.loads(response.text)
    except json.JSONDecodeError:
        print(" Initial JSON parsing failed. Trying regex-based fallback...")
        match = re.search(r'\[\s*{[\s\S]*?}\s*\]', response.text)

        if match:
            try:
                raw_test_cases = json.loads(match.group())
            except Exception as e:
                return f" Failed to parse extracted JSON: {e}\nExtracted:\n{match.group()}"
        else:
            return f" Failed to find any JSON array in LLM response.\nRaw:\n{response.text}"

    # Validate structure of test cases
    for case in raw_test_cases:
        if "input" not in case or "expected_output" not in case:
            return f"❌ Malformed test case detected: {case}"

    # Prepare input-output arrays
    inputs = [case["input"][0] if len(case["input"]) == 1 else case["input"] for case in raw_test_cases]
    outputs = [case["expected_output"] for case in raw_test_cases]

    formatted_data = {
        "file_name": file_name,
        "inputs": inputs,
        "outputs": outputs
    }

    testcases_file = "testcases.json"

    # Load or initialize the file
    if os.path.exists(testcases_file):
        with open(testcases_file, "r") as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    # Remove duplicates by file name
    existing_data = [entry for entry in existing_data if entry["file_name"] != file_name]
    existing_data.append(formatted_data)

    # Write updated test cases
    with open(testcases_file, "w") as f:
        json.dump(existing_data, f, indent=2)

    return "✅ Test cases generated and stored successfully."
