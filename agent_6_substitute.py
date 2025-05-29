import os
import json
import google.generativeai as genai  # type: ignore

genai.configure(api_key="#YOUR API KEY HERE")

SYSTEM_INSTRUCTION = """
You are a precise Python testing assistant.

Your task is to take a Python function and a list of test cases (input/output pairs), and determine if the function passes all the test cases.

Instructions:
- Evaluate each test case using the function.
- If all test cases pass (outputs match), return only: `true`
- If any test fails, return only: `false`, followed by a JSON list of the failed test cases with the input, expected output, and actual output.

Be strict — outputs must match exactly.
Do not explain, just return the evaluation result.
"""

generation_config = {
    'temperature': 0.3,
    'top_p': 0.95,
    "top_k": 40,
    "max_output_tokens": 400,
    "response_mime_type": "text/plain"
}

agent_6 = genai.GenerativeModel(
    model_name='gemini-2.0-flash-exp',
    generation_config=generation_config,
    system_instruction=SYSTEM_INSTRUCTION
)

chat_session = agent_6.start_chat()

# File to store bug history
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

# Agent 6: LLM-based test executor
def test_code_llm(file_name: str,code: str,test_case_file: str):
    

    with open(test_case_file, "r") as f:
        all_test_cases = json.load(f)
    abs_file_name = os.path.abspath(file_name)
    file_test_cases = [tc for tc in all_test_cases if os.path.abspath(tc["file_name"]) == abs_file_name]


    if not file_test_cases:
        return False, "No test cases found for this file."

    # Format test case content
    test_inputs_outputs = []
    for case in file_test_cases:
        inputs = case["inputs"]
        outputs = case["outputs"]
        for i, test_input in enumerate(inputs):
            test_inputs_outputs.append({
                "input": test_input,
                "expected_output": outputs[i]
            })

    prompt = f"""
    Python code:
    \"\"\"
    {code}
    \"\"\"

    Test cases:
    {json.dumps(test_inputs_outputs, indent=2)}

    Evaluate whether the function passes all test cases.
    Remember: Only return `true` if all passed. If not, return `false` and the list of failed cases.
    """

    response = chat_session.send_message(prompt)
    result = response.text.strip()

    # Try to parse result
    if result.lower().startswith("true"):
        return True, []
    elif result.lower().startswith("false"):
        try:
            json_part = result[result.find("["):]
            failed_cases = json.loads(json_part)
            return False, failed_cases
        except:
            return False, "Could not parse failure details."
    else:
        return False, f"Unexpected response: {result}"
