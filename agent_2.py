import os
import json
import google.generativeai as genai # type: ignore

genai.configure(api_key="#YOUR API KEY HERE")

# Chain Prompting System Instruction
SYSTEM_INSTRUCTION = """
You are a highly skilled code assistant. Your task is to analyze code, detect bugs or potential issues, and provide clear, actionable feedback using a structured reasoning process.

Follow these steps:

Step 1: Carefully read and understand the full code snippet.
Step 2: Identify the **exact line number(s)** where a bug or issue occurs.
Step 3: For each issue, explain clearly and concisely:
    - What the bug or issue is.
    - Why it would cause failure, incorrect behavior, or poor performance.
    - Build a clear logical argument for why this is considered a bug or issue.
    - If relevant, mention how it might behave differently in edge cases or production environments.

Only return output in **this exact format**:

- Line X: [line number]
- Explanation: [Detailed explanation of the issue and its consequences, with logical reasoning]


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

# File to store bug history
HISTORY_FILE = "bug_history.json"

# Load history if it exists
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        bug_history = json.load(f)
else:
    bug_history = {}

# Save history to disk
def save_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump(bug_history, f, indent=2)

# Main function to detect bugs
# Takes file_name as key and code as string
def detect_code_bug(file_name: str, code: str) -> str:
    

    numbered_code = add_line_numbers(code)
    prompt = f"""
    You are a highly skilled code assistant. Your task is to analyze the following Python code, detect the single line containing a bug or potential issue, and provide clear, structured feedback using a reasoning-based approach.

    Follow these steps carefully:

    Step 1: Read and understand the entire code.
    Step 2: Identify the **exact single line number** where a bug or problematic behavior exists.
    Step 3: Explain your reasoning step by step:
    - What exactly is on that line.
    - Why it is problematic — describe the logic behind identifying it as a bug.
    - What kind of failure, incorrect behavior, or unexpected output this bug could cause.

    Use this **exact output format**:

    - Line X: [line number where the issue is]
    - Explanation: [Step-by-step reasoning with a clear explanation of the bug]

    Example (for illustration):

    1  user_input = input("Do you want to continue? ")
    2  if user_input = "yes":
    3      print("Continuing...")
    4  else:
    5      print("Stopping.")

    Example Output (for illustration):

    - Line 2: `if user_input = "yes":`
    - Explanation: The single equals sign `=` is used here, which is the assignment operator in Python, not a comparison operator. Conditional statements require a comparison using `==` to check equality. Using `=` inside an `if` statement causes a `SyntaxError`, preventing the program from running. This is a fundamental syntax rule in Python, and correcting it to `if user_input == "yes":` fixes the issue.

    Now, keeping in mind all the instructions and that the bug is only in one line, analyze the following Python code:

    
    {numbered_code}
    


    """


    response = chat_session.send_message(prompt)
    result = response.text

    

    return result
