import os
import json
import google.generativeai as genai # type: ignore

genai.configure(api_key="#YOUR API KEY HERE")

# Chain Prompting System Instruction
SYSTEM_INSTRUCTION= """
You are an expert bug classification assistant.

Your task is to analyze a given buggy code snippet along with a detailed bug explanation from a prior analysis, and classify the bug into one of the predefined bug types.

Follow these steps:

Step 1: Carefully read and fully understand both the buggy code and the bug explanation.
Step 2: Determine the single best matching bug type from the following list:

- Incorrect assignment operator
- Incorrect variable
- Incorrect comparison operator
- Missing condition
- Missing/added +1
- Variable swap
- Incorrect array slice
- Variable prepend
- Incorrect data structure constant
- Incorrect method called
- Incorrect field dereference
- Missing arithmetic expression
- Missing function call
- Missing line

Step 3: Provide a concise and clear explanation supporting why this bug fits the selected type, referencing the code behavior or explanation provided.

Your response must strictly follow this format:

Bug Type: [chosen bug type exactly as above]  
Reasoning: [clear and logical explanation for your classification]

Do not include any other text or commentary.
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


def detect_code_bug_type(file_name: str, code: str, agent_1_output: str = None) -> tuple[str, str]:
    

    numbered_code = add_line_numbers(code)
    BUG_TYPES = {
    "Incorrect assignment operator": "Using '=' instead of '==' or vice versa in expressions or conditions.",
    "Incorrect variable": "Using the wrong variable name or referencing a variable that doesn't hold the intended data.",
    "Incorrect comparison operator": "Using the wrong comparison operator such as '<' instead of '<=' or mixing 'is' vs '==' incorrectly.",
    "Missing condition": "A required condition in control flow (if/while) is omitted.",
    "Missing/added +1": "Off-by-one errors where an increment or decrement is missing or wrongly added.",
    "Variable swap": "Two variables are swapped or assigned incorrectly, reversing their intended roles.",
    "Incorrect array slice": "Array or list slicing with wrong indices causing wrong subsections to be taken.",
    "Variable prepend": "Incorrectly adding a prefix or suffix to variable names or values.",
    "Incorrect data structure constant": "Using wrong constants or literals for data structures like [] vs () vs {}.",
    "Incorrect method called": "Calling a wrong method or function not intended for the object.",
    "Incorrect field dereference": "Accessing a wrong attribute or property on an object.",
    "Missing arithmetic expression": "An arithmetic operation is missing or incomplete.",
    "Missing function call": "A function is referenced but not actually called (missing parentheses).",
    "Missing line": "A necessary line of code is missing entirely from the logic."
}

    prompt = f"""
    You are a specialized bug classification assistant.

    Your inputs:
    1. A snippet of buggy Python code.
    2. A detailed bug explanation produced by a prior agent analyzing the code.

    Your task:
    - Carefully analyze both inputs.
    - Determine which one of the following 14 bug types best describes the bug in the code.
    - Each bug type is described briefly here to aid your understanding:

    {chr(10).join(f"{k}: {v}" for k, v in BUG_TYPES.items())}

    - Provide ONLY two things in your output:

    1. The bug type from the list above (choose exactly one).
    2. A concise but clear explanation of WHY you classified the bug as that type, referencing the code behavior or explanation given.

    DO NOT output anything else — no extra commentary or unrelated information.

    ---

    Example format:

    Bug Type: Incorrect assignment operator  
    Reasoning: The bug explanation states that the code uses '=' in a condition instead of '==', which is an assignment operator mistake, directly matching the 'Incorrect assignment operator' category.

    ---

    Now classify the following:

    Buggy code:
    \"\"\"
    {numbered_code}
    \"\"\"

    Bug explanation:
    \"\"\"
    {agent_1_output}
    \"\"\"
    """
    print("hek")



    response = chat_session.send_message(prompt)
    result = response.text

    # Split into two parts: Bug Type and Reasoning
    lines = result.splitlines()
    bug_type_line = next((line for line in lines if line.startswith("Bug Type:")), None)
    reasoning_line = next((line for line in lines if line.startswith("Reasoning:")), None)

    if bug_type_line is None or reasoning_line is None:
        raise ValueError(f"Unexpected response format:\n{result}")

    bug_type = bug_type_line.replace("Bug Type:", "").strip()
    reasoning = reasoning_line.replace("Reasoning:", "").strip()

    
    
    
    return bug_type,reasoning

