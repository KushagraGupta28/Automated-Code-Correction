import os
import glob
import re
import json
import time
import google.generativeai as genai  # type: ignore
import google.api_core.exceptions  # type: ignore
from google.api_core.exceptions import ResourceExhausted# type: ignore
import time
# Configure API key
genai.configure(api_key="#YOUR API KEY HERE")

generation_config = {
    'temperature': 0.3,
    'top_p': 0.8,
    'top_k': 20,
    'max_output_tokens': 512,
    'response_mime_type': 'text/plain'
}


bug_classifier = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    generation_config=generation_config,
    system_instruction="""
You are a bug classification assistant. You will be given **buggy Python code with line numbers**. Your task is to:

1. Carefully analyze the given code.
2. Identify the type of bug in the code using only the following list of 14 bug types.
3. Assume there is always **exactly one bug** in the input code.
4. Return your output strictly in the following JSON format:

{
  "bug_type": "<one of the 14 types below>"
}

Valid bug types:
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

🧠 Use logic and context to identify how the bug affects the code.
❌ Do not explain the answer or modify the code.
✅ Return only the bug type in JSON format.

If the code looks fine, still pick the **most likely bug** from the list.

Example:

Input:
1. def add_one(x):  
2.     return x + 2  

Output:
{
  "bug_type": "Missing/added +1"
}
"""
)

bug_fixer = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    generation_config=generation_config,
    system_instruction= """
You are a bug fixing assistant. You will be given Python code with exactly one bug in it, along with the type of bug.

Your task is to:
1. Carefully understand the code and the provided bug type.
2. Fix the bug in the code.
3. Return ONLY the corrected code — do not explain the changes or include any extra text.

You must fix one of the following 14 bug types:
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

The input will always contain:
- A `bug_type` field (with one of the 14 types above)
- Python code with the bug

Think carefully and return the fixed code in proper Python syntax.

Output format:
Return ONLY the fixed code. No explanations, no JSON, no markdown — just valid Python code.

Example Input:
bug_type: Missing/added +1  
code:
1. def add_one(x):  
2.     return x + 2

Example Output:
def add_one(x):
    return x + 1

"""

)



bug_verify = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    generation_config=generation_config,
    system_instruction= """
You are a code validation assistant. You will be given Python code that has supposedly been fixed.

Your task is to:
1. Carefully analyze the provided Python code.
2. Detect if there is exactly one bug still present in the code.
3. Identify the type of the bug if found, choosing from the following 14 bug types:

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

4. If a bug is found, return ONLY a JSON object with the bug type in this format:
{
  "bug_type": "..."
}

5. If no bugs are found, return ONLY the JSON object:
{
  "bug_type": "No bug"
}

Important:
- Do NOT provide explanations or any text other than the JSON response.
- Do NOT include line numbers or code snippets.
- The input will only contain the fixed Python code.

Think carefully and return your result in the exact JSON format described above.
"""
)

base_system_prompt = """
You are a bug detection agent. You will be given buggy Python code with line numbers. Your task is to:

1. Carefully analyze the code.
2. Identify the type of bug it contains.
3. Return your result in JSON format like this:
{
  "bug_type": "..."
}

⚠️ Important Rules:
- Choose exactly ONE bug type from the list below.
- Always assume there is exactly one bug in the code.
- Do NOT include line numbers in your output.
- Do NOT add any extra explanation or comments.
- Output ONLY the JSON — nothing else.

Valid Bug Types (with descriptions):

1. Incorrect assignment operator — Using '=' instead of '==' or vice versa.
2. Incorrect variable — A wrong variable name is used in logic.
3. Incorrect comparison operator — Using '<', '>', etc. incorrectly.
4. Missing condition — An `if` or similar condition is absent.
5. Missing/added +1 — Off-by-one error in loops, indices, etc.
6. Variable swap — Two variables are used in the wrong order.
7. Incorrect array slice — Slicing syntax or bounds are incorrect.
8. Variable prepend — A prefix like `self.` or parameter is missing.
9. Incorrect data structure constant — Wrong default literal like `{}` vs `[]`.
10. Incorrect method called — Wrong function/method name used.
11. Incorrect field dereference — Incorrect object property is accessed.
12. Missing arithmetic expression — A needed operation is missing (`+`, `-`, etc.).
13. Missing function call — A function is mentioned but not invoked.
14. Missing line — A critical line of logic is entirely missing.

🔍 Examples:

Code:
1. def is_even(n):
2.     return n % 2 = 0

Output:
{
  "bug_type": "Incorrect assignment operator"
}

Code:
1. def gcd(a, b):
2.     if b == 0:
3.         return a
4.     else:
5.         return gcd(a % b, b)

Output:
{
  "bug_type": "Incorrect variable"
}

Now analyze this code:
"""



FIXER_PROMPT = """
You are a bug-fixing assistant. You will be given:

- Buggy Python code
- The type of bug it contains (from a predefined list)

Your job is to:
- Analyze the buggy code
- Fix the code based ONLY on the given bug type
- Return only the fixed code (without explanation, comments, or extra formatting)

Here are the 14 bug types you can encounter and how to fix them:

1. Incorrect assignment operator — Fix incorrect usage of '=' vs '==' or similar assignment logic.
2. Incorrect variable — Replace the wrong variable used with the correct one based on context.
3. Incorrect comparison operator — Replace operators like '<', '>', '==', etc., with the correct one.
4. Missing condition — Add an if/else condition that is logically required.
5. Missing/added +1 — Fix off-by-one errors, such as loop indices or ranges.
6. Variable swap — Swap two variables that were incorrectly ordered.
7. Incorrect array slice — Correct the slicing bounds or syntax of lists or arrays.
8. Variable prepend — Add a variable (e.g., 'self.' or function argument) that was missing before usage.
9. Incorrect data structure constant — Fix incorrect usage of default values (e.g., using {{}} vs [] or 0).
10. Incorrect method called — Replace the incorrect function or method with the correct one.
11. Incorrect field dereference — Fix incorrect access of an object attribute or field.
12. Missing arithmetic expression — Add a necessary operation like '+', '-', '*', etc.
13. Missing function call — Call a function that was referenced but not invoked.
14. Missing line — Insert the missing line needed for the code to work properly.

Example 1:
Bug Type: Incorrect variable  
Code:
```python
def square(n):
    return x * x
```

Fix:
```python
def square(n):
    return n * n
```

Example 2:
Bug Type: Missing function call  
Code:
```python
def length(lst):
    return lst
```

Fix:
```python
def length(lst):
    return len(lst)
```

Now fix this:
Bug Type: {bug_type}  
Code:
```python
{buggy_code}
```

Return only the fixed code. 
"""

VALIDATOR_PROMPT = """
You are a code validation assistant. You will be given Python code that has supposedly been fixed.

Your task is to:
1. Carefully analyze the provided Python code.
2. Detect if there is exactly one bug still present in the code.
3. Identify the type of the bug if found, choosing from the following 14 bug types:

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

4. If a bug is found, return ONLY a JSON object with the bug type in this format:
{
  "bug_type": "..."
}

5. If no bugs are found, return ONLY the JSON object:
{
  "bug_type": "No bug"
}

Important:
- Do NOT provide explanations or any text other than the JSON response.
- Do NOT include line numbers or code snippets.
- The input will only contain the fixed Python code.

Think carefully and return your result in the exact JSON format described above.
"""
# Utility to add line numbers
def add_line_numbers(code: str) -> str:
    return '\n'.join([f"{i+1}. {line}" for i, line in enumerate(code.splitlines())])

# Utility to safely extract JSON response
def extract_bug_info(text: str):
    try:
        match = re.search(r'\{.*?\}', text, re.DOTALL)
        if match:
            json_text = match.group()
            return json.loads(json_text)
    except json.JSONDecodeError:
        return {"bug_type": "ParseError"}
    return {"bug_type": "None"}


def fix_buggy_code(my_bot, buggy_code: str, bug_type: str) -> str:
    prompt = FIXER_PROMPT.format(
        bug_type=bug_type,
        buggy_code=buggy_code.strip()
    )
    chat = my_bot.start_chat()
    response = chat.send_message(prompt)
    return response.text.strip()


# Chat session with memory
history = []
print("bot : HELLO, HOW CAN I HELP YOU")
chat_session = bug_classifier.start_chat(history=history)


def run_agent_3_validator(agent, fixed_code: str) -> tuple[bool, str | None]:
    """
    Agent 3: Runs bug detection on fixed code to check if bugs remain.
    Returns (True, None) if code is bug-free,
    Returns (False, bug_type) if a bug is detected.
    """

    prompt = VALIDATOR_PROMPT + "\n\n" + fixed_code.strip()

    chat = agent.start_chat()
    response = chat.send_message(prompt)
    response_text = response.text.strip()

    # Extract bug_type from JSON response
    import re
    import json

    try:
        # Strip markdown-style formatting like ```json ... ```
        cleaned_response = re.sub(r"```(?:json)?|```", "", response_text.strip()).strip()
        bug_info = json.loads(cleaned_response)
        bug_type = bug_info.get("bug_type", None)
    except Exception as e:
        print(f"Error parsing agent 3 response: {e}")
        print(f"Response was: {response_text}")
        return False, "Parsing error"

    if bug_type and bug_type != "No bug":
        print(f"Agent 3 found a bug: {bug_type}")
        return False, bug_type
    else:
        print("Agent 3 found no bugs in fixed code.")
        return True, None

    


def process_files_in_folder(folder_path: str, save_folder: str, max_files=50):
    py_files = glob.glob(os.path.join(folder_path, '*.py'))
    py_files = py_files[:max_files]

    print(f"Found {len(py_files)} Python files. Processing up to {max_files} files...\n")

    
    os.makedirs(save_folder, exist_ok=True)

    for i, file_path in enumerate(py_files, 1):
        print(f"Processing file {i}: {file_path}")
        try:
            with open(file_path, 'r') as f:
                code = f.read()
        except Exception as e:
            print(f"Failed to read {file_path}: {e}")
            continue

        numbered_code = add_line_numbers(code)
        full_prompt = base_system_prompt + numbered_code
        model_response = None  
        # Retry up to 3 times if rate limited
        for attempt in range(3):
            try:
                response = chat_session.send_message(full_prompt)
                model_response = response.text  # Assign the response
                break  # Exit loop if successful
            except ResourceExhausted:
                wait_time = 30 * (attempt + 1)
                print(f"Rate limit hit. Waiting {wait_time} seconds... (Attempt {attempt + 1}/3)")
                time.sleep(wait_time)
            except Exception as e:
                print(f"Unexpected error during model call: {e}")
                break  # Don't retry on unknown errors

        # After loop ends, check if we got a response
            if model_response is None:
                print("Failed to process after multiple retries. Skipping this file.\n")
                continue

        history.append({"user": code, "bot": model_response})

        bug_result = extract_bug_info(model_response)
        bug_type = bug_result.get("bug_type")

        print(f"Detected bug type: {bug_type}\n")
        
        fixed_code = fix_buggy_code(bug_fixer, numbered_code, bug_type)
            
        is_fixed, new_bug_type = run_agent_3_validator(bug_verify,fixed_code)

        if is_fixed:
            # Save the fixed code, no further fixing needed
            filename = os.path.basename(file_path)
            save_path = os.path.join(save_folder, filename)
            with open(save_path, 'w') as f_out:
                f_out.write(fixed_code)
            print(f"✅ Bug fixed and code saved to {save_path}\n")
        else:
            # If bug remains, send the code back to Agent 2 with new bug type
            print(f"Agent 3 detected bug in fixed code, re-fixing with bug: {new_bug_type}")
            fixed_code_2 = fix_buggy_code(bug_fixer,fixed_code, new_bug_type)

            # Optional: validate again or save as is
            # For simplicity, save after second fix attempt
            filename = os.path.basename(file_path)
            save_path = os.path.join(save_folder, filename)
            with open(save_path, 'w') as f_out:
                f_out.write(fixed_code_2)
            print(f"🔄 Code re-fixed and saved to {save_path}\n")
            # Save the fixed code to the new folder with .py extension
            original_filename = os.path.basename(file_path)
            filename_without_ext = os.path.splitext(original_filename)[0]
            save_path = os.path.join(save_folder, filename_without_ext + ".py")
            with open(save_path, 'w') as f_out:
                f_out.write(fixed_code)
            print(f"Saved fixed code to {save_path}\n")

    






# Entry point
if __name__ == "__main__":
    folder_path = 'C:/Users/mitaksh/OneDrive/Desktop/RESEARCH INTERN/Code-Refactoring-QuixBugs/python_programs'
    save_folder = 'C:/Users/mitaksh/OneDrive/Desktop/RESEARCH INTERN/Code-Refactoring-QuixBugs/fixed_programs'
    if not os.path.isdir(folder_path):
        print("Invalid folder path. Please check and try again.")
    else:
        process_files_in_folder(folder_path,save_folder)


