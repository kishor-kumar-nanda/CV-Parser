import os
import pdfplumber
from docx import Document
import openai
import json

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")  # or replace with your key directly

def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

def clean_text(text):
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())

def create_prompt(cv_text):
    return f"""
Extract the following information from this resume:
- name
- email
- phone
- skills
- education
- work experience
- projects
- certifications

Format the output as a JSON object using these exact keys.

Resume:
\"\"\"
{cv_text}
\"\"\"
"""

def extract_cv_data(text):
    prompt = create_prompt(text)
    response = openai.ChatCompletion.create(
        model="gpt-4",  # or "gpt-3.5-turbo"
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response['choices'][0]['message']['content']

def parse_json_response(response):
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        print("Invalid JSON response. Raw output:")
        print(response)
        return {}

def process_cv(file_path):
    if file_path.endswith(".pdf"):
        raw_text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        raw_text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file type. Use PDF or DOCX.")

    cleaned_text = clean_text(raw_text)
    model_response = extract_cv_data(cleaned_text)
    return parse_json_response(model_response)

if __name__ == "__main__":
    file_path = input("Enter path to CV (PDF/DOCX): ")
    data = process_cv(file_path)
    print("\nExtracted JSON:")
    print(json.dumps(data, indent=2))
