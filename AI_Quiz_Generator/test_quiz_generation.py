import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import generate_quiz_from_text, extract_text

# Test text extraction and quiz generation
test_text = """
Python is a high-level programming language. It was created by Guido van Rossum and first released in 1991.
Python supports multiple programming paradigms including procedural, object-oriented, and functional programming.
It has dynamic typing and automatic memory management.
"""

print("Testing text extraction...")
print(f"Test text: {test_text[:100]}...")

print("\nTesting quiz generation...")
try:
    questions = generate_quiz_from_text(test_text, 3)
    print(f"Generated {len(questions)} questions:")
    for i, q in enumerate(questions):
        print(f"Question {i+1}: {q.get('question', 'No question')}")
        print(f"Options: {q.get('options', 'No options')}")
        print(f"Correct Answer: {q.get('correct_answer', 'No correct answer')}")
        print("---")
except Exception as e:
    print(f"Error generating questions: {e}")
    import traceback
    traceback.print_exc()
