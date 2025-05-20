import os
from openai import OpenAI
from dotenv import load_dotenv

# Load .env if needed
load_dotenv()

# Local Ollama LLM endpoint
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

def generate_test_cases(raw_lines):
    prompt = f"""You are an expert QA test script analyzer. Below is a raw export of lines from a multi-sheet Excel workbook used in Oracle ERP testing.

Your task is to extract and reformat this into clear test steps. Each step should include an action, and optionally an expected result. If you detect sections belonging to different test cases, break them accordingly.

Respond in the following format:

TEST CASE: <Name>
- Step 1: <Action> → <Expected Result>
- Step 2: ...
...

Here is the raw content:
{raw_lines}
"""

    response = client.chat.completions.create(
        model="mistral",
        messages=[
            { "role": "system", "content": "You are an expert QA automation assistant. You convert raw ERP test instructions into structured, step-by-step test cases." },
            { "role": "user", "content": prompt }
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    # Example usage with sample lines
    raw_lines = """
[Summary] PO-001 | Create Supplier
[Summary] PO-002 | Update Supplier
[Create Supplier] Step 1: Login to Oracle
[Create Supplier] Step 2: Navigate to Procurement > Suppliers
[Create Supplier] Step 3: Click 'Create Supplier'
[Create Supplier] Step 4: Fill in supplier details
[Create Supplier] Step 5: Click Submit
"""
    output = generate_test_cases(raw_lines)
    print(output)