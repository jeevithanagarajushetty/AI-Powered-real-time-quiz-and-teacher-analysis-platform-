import sys
sys.path.append('.')
from app import quiz_collection, quiz_codes_collection
from datetime import datetime, timedelta
import uuid

# Create a simple test quiz
questions = [
    {
        'question': 'What is Python?',
        'options': ['Snake', 'Programming language', 'Car', 'Planet'],
        'correct_answer': 1,
        'explanation': 'Python is a programming language.'
    },
    {
        'question': 'Which keyword is used to define a function in Python?',
        'options': ['function', 'def', 'func', 'define'],
        'correct_answer': 1,
        'explanation': 'The def keyword is used to define functions.'
    }
]

quiz_code = 'TEST123'
quiz_data = {
    'title': 'Test Python Quiz',
    'subject': 'Python Programming',
    'questions': questions,
    'duration_minutes': 30,
    'teacher_id': 'test_teacher',
    'quiz_code': quiz_code,
    'created_at': datetime.now(),
    'status': 'active'
}

result = quiz_collection.insert_one(quiz_data)
print(f'Quiz inserted with ID: {result.inserted_id}')

quiz_codes_collection.insert_one({
    'quiz_id': str(result.inserted_id),
    'quiz_code': quiz_code,
    'created_at': datetime.now(),
    'expires_at': datetime.now() + timedelta(days=30),
    'is_active': True
})

print(f'Test quiz created with code: {quiz_code}')
