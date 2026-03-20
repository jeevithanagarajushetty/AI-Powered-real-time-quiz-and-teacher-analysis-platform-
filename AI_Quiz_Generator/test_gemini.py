import google.genai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

client = genai.Client(api_key=GEMINI_API_KEY)

test_text = 'Python is a high-level programming language created by Guido van Rossum. It supports multiple programming paradigms including procedural, object-oriented, and functional programming. Python is widely used in web development, data science, and artificial intelligence.'

prompt = f'''Create 2 multiple choice questions from the text below.

Return ONLY valid JSON array.

Format example:
[
  {{
    "question": "What is Python?",
    "options": ["Snake", "Programming language", "Car", "Planet"],
    "correct_answer": 1,
    "explanation": "Python is a programming language."
  }}
]

TEXT:
{test_text}'''

try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    
    print('Raw response:')
    print(response.text)
    print('\n' + '='*50 + '\n')
    
    raw = response.text.strip()
    raw = raw.replace('```json', '').replace('```', '').strip()
    raw = raw.replace('\n', '').replace('\r', '').strip()
    
    start = raw.find('[')
    end = raw.rfind(']') + 1
    
    if start != -1 and end != -1:
        json_text = raw[start:end]
        print(f'Parsed JSON: {json_text}')
        
        import json
        questions = json.loads(json_text)
        print(f'\nGenerated {len(questions)} questions:')
        for i, q in enumerate(questions, 1):
            print(f'Q{i}: {q.get("question", "N/A")}')
            print(f'Options: {q.get("options", "N/A")}')
            print(f'Correct: {q.get("correct_answer", "N/A")}')
            print('---')
    else:
        print('No JSON found in response')
        
except Exception as e:
    print(f'Error: {e}')
