import random
import re

def generate_quiz(text, num_questions, difficulty):
    """
    Generate quiz questions from text using a simple rule-based approach
    """
    try:
        num_questions = int(num_questions)
        text = text[:800]  # Limit text size
        
        # Simple question generation based on text content
        questions = []
        
        # Extract key sentences from text
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if not sentences:
            sentences = [text]  # Use full text if no sentences found
        
        for i in range(min(num_questions, len(sentences))):
            sentence = sentences[i % len(sentences)]
            
            # Create question from sentence
            question = f"What is the main concept discussed in: {sentence[:50]}..."
            
            # Generate options
            options = [
                sentence[:30] + "...",
                "Alternative option A",
                "Alternative option B", 
                "Alternative option C"
            ]
            
            # Shuffle options
            random.shuffle(options)
            correct_answer = options.index(sentence[:30] + "...")
            
            questions.append({
                'question': question,
                'options': options,
                'correct_answer': correct_answer,
                'explanation': f'This question is based on the text: {sentence[:100]}...'
            })
        
        # Format as quiz string
        quiz = ""
        for i, q in enumerate(questions, 1):
            quiz += f"Q{i}: {q['question']}\n"
            for j, option in enumerate(q['options']):
                quiz += f"   {chr(65+j)}. {option}\n"
            quiz += f"\n"
        
        return quiz
        
    except Exception as e:
        print(f"Error generating quiz: {e}")
        return f"Error generating quiz: {str(e)}"