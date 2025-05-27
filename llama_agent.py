import requests

url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer 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"
}

conversation = [
    {
        "role": "system",
        "content": """You are a bug classification assistant. You will be given **buggy Python code with line numbers**. Your task is to:

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
}"""
    }
]

def add_line_numbers(code: str) -> str:
    return '\n'.join([f"{i+1}. {line}" for i, line in enumerate(code.splitlines())])

def chat_with_llm(user_input):
    conversation.append({"role": "user", "content": user_input})
    
    data = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": conversation
    }
    
    response = requests.post(url, headers=headers, json=data)
    response_json = response.json()
    
    assistant_message = response_json['choices'][0]['message']['content']
    
    conversation.append({"role": "assistant", "content": assistant_message})
    
    return assistant_message

print("Bug classification assistant ready! Type 'quit' to exit.\n")

while True:
    file_path = input("Enter Python file path (or 'quit' to exit): ").strip()
    if file_path.lower() == "quit":
        break
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except Exception as e:
        print(f"Failed to read file: {e}\n")
        continue
    
    numbered_code = add_line_numbers(code)
    print("\nNumbered code sent for classification:\n")
    print(numbered_code)
    print("\nAnalyzing bug...\n")
    
    result = chat_with_llm(numbered_code)
    print("Bug classification result:", result, "\n")
