import os
import json
import google.generativeai as genai  # type: ignore

genai.configure(api_key="#YOUR API KEY HERE")

SYSTEM_INSTRUCTION = """
You are an expert software analyst.

Your task is to carefully analyze the provided Python code snippet — which may contain bugs or issues — and clearly describe the main purpose or function of the code.

Focus on:
- What the code is trying to achieve.
- The main operations or logic it implements.
- The role of key functions or code blocks, if identifiable.
- Avoid mentioning bugs or errors; focus solely on the intended functionality.
- Use clear, concise language suitable for someone planning test cases.

Output only the purpose description as a short paragraph.

Example:
If the code’s main function is to reverse a string, your output should be:

"The code takes an input string and returns a new string with the characters in reverse order. It processes the string by iterating from the end to the beginning, effectively reversing the character sequence."
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

# Utility to add line numbers to code
def add_line_numbers(code: str) -> str:
    return '\n'.join([f"{i+1}. {line}" for i, line in enumerate(code.splitlines())])

# File to store history
HISTORY_FILE = "bug_history.json"

# Load history if it exists, otherwise start fresh list
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        bug_history = json.load(f)
else:
    bug_history = []

# Save history to disk
def save_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump(bug_history, f, indent=2)

# Main function to detect code purpose
def detect_code_purpose(file_name: str) -> str:
    with open(file_name, "r") as f:
        code = f.read()

    numbered_code = add_line_numbers(code)
    
    prompt = f"""
    Analyze the following Python code snippet:

    \"\"\" 
    {numbered_code}
    \"\"\"

    Describe clearly and concisely the main purpose and function of this code. Focus on what the code is intended to do, ignoring any bugs or errors it may contain.

    Output only a short paragraph describing the code's purpose.

    Example:
    If the code’s main function is to reverse a string, your output should be:

    "The code takes an input string and returns a new string with the characters in reverse order. It processes the string by iterating from the end to the beginning, effectively reversing the character sequence."
    """

    response = chat_session.send_message(prompt)
    result = response.text.strip()

    
    return numbered_code,result
