import os
import json
import google.generativeai as genai  # type: ignore

genai.configure(api_key="#YOUR API KEY HERE")

SYSTEM_INSTRUCTION = """
You are a highly skilled Python code repair assistant.

Your task is to take:
- A buggy Python code snippet,
- A detailed bug explanation,
- A classified bug type,
- A brief description of the code's purpose,
- (Optional) Failing test cases,

... and fix the **one and only one line** of code that is buggy.

Follow this strict process:
1. Read and fully understand the original buggy code.
2. Study the provided bug explanation and bug type to identify the exact line that contains the bug.
3. Replace only that **one single line** with the correct version.
4. Do not rewrite or change any other lines, including docstrings, indentation, or structure.
5. Ensure your fix matches the described purpose and passes all test cases if given.

⚠️ RULES:
- You MUST modify exactly one line and only one line.
- DO NOT rewrite or reformat the whole function.
- DO NOT add comments or explanations.
- DO NOT remove or alter surrounding lines or docstrings.
- Output ONLY the corrected code.

Return the complete code with the single-line fix applied.
"""
def add_line_numbers(code: str) -> str:
    return '\n'.join([f"{i+1}. {line}" for i, line in enumerate(code.splitlines())])

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

HISTORY_FILE = "bug_history.json"

# Load history from disk
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        bug_history = json.load(f)
else:
    bug_history = {}

# Save history to disk
def save_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump(bug_history, f, indent=2)

# Utility to add line numbers to code
def add_line_numbers(code: str) -> str:
    return '\n'.join([f"{i+1}. {line}" for i, line in enumerate(code.splitlines())])

# Main function that uses history only
def fixed_code(file_name: str,code: str) -> str:
    if file_name in bug_history and "fixed_code" in bug_history[file_name]:
        return bug_history[file_name]["fixed_code"]

    # Retrieve all required fields from bug_history
    entry = bug_history.get(file_name, {})
    #numbered_code = entry.get("code")
    bug_explanation = entry.get("bug_report")
    bug_type = entry.get("bug_type")
    purpose = entry.get("purpose")
    failed_cases = entry.get("failed_test_cases")

    numbered_code = add_line_numbers(code)

    

    # Base prompt
    prompt = f"""
    You are provided with:

    1. Buggy Python code:
    \"\"\" 
    {numbered_code}
    \"\"\" 

    2. Bug explanation:
    \"\"\" 
    {bug_explanation}
    \"\"\" 

    3. Bug classification:
    \"\"\" 
    {bug_type}
    \"\"\" 

    4. Code purpose:
    \"\"\" 
    {purpose}
    \"\"\" 
    """

    

    prompt += """
    INSTRUCTIONS:

    - The bug exists in exactly ONE LINE.
    - Fix ONLY that one line.
    - Do NOT modify, delete, or reformat any other lines.
    - Keep comments, whitespace, indentation, and structure identical to the original.
    - Output only the corrected full Python code — nothing else.
    - Do NOT include line numbers, quotation marks, code blocks (like ```python), or any commentary.
    - Do NOT include extra blank lines or markdown formatting.
    - REMOVE ALL EXISTING COMMENTS in the code.
    - DO NOT GIVE THE NUMBERED CODE AS OUTPUT , REMOVE THE LINE NUMBERS BEFORE OUTPUTTING
    Your output should be clean, plain Python code.

    dont return none , give the correct code 
    """



    response = chat_session.send_message(prompt)
    result = response.text.strip()

    
    return result
