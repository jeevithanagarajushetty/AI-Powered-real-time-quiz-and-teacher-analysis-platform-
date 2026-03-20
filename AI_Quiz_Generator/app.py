"""
AI Quiz Platform - Updated Version
Uses Google Gemini API for quiz generation
"""

from flask import Flask, render_template, request, redirect, session, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import uuid
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

import google.generativeai as genai
import google.ai.generativelanguage as glm
import pdfplumber
import docx

# ==============================
# LOAD ENVIRONMENT VARIABLES
# ==============================

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = "ai_quiz_platform"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ==============================
# GEMINI CONFIG
# ==============================

genai.configure(api_key=GEMINI_API_KEY)
print("Gemini API KEY Loaded:", GEMINI_API_KEY)

# ==============================
# DATABASE
# ==============================

mongo_client = MongoClient(MONGODB_URI)
db = mongo_client[DATABASE_NAME]

users_collection = db["users"]
quiz_collection = db["quiz"]
quiz_codes_collection = db["quiz_codes"]
quiz_attempts_collection = db["quiz_attempts"]

# ==============================
# APP CONFIG
# ==============================

app = Flask(__name__)
app.secret_key = "super-secret-key"

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==============================
# HELPER FUNCTIONS
# ==============================

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text(filepath):

    text = ""

    if filepath.endswith(".txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

    elif filepath.endswith(".pdf"):
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

    elif filepath.endswith(".docx"):
        document = docx.Document(filepath)
        for para in document.paragraphs:
            text += para.text

    return text


# 1. FIX MODEL NAME AND PARSING
def generate_quiz_from_text(text, num_questions):
    # First try Gemini API
    try:
        prompt = f"""
        Create {num_questions} multiple choice questions from the text below.
        Return ONLY a valid JSON array.
        Format: [{{"question": "...", "options": ["a", "b", "c", "d"], "correct_answer": 0, "explanation": "..."}}]
        TEXT: {text[:4000]}
        """
        # Use correct Gemini API call
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        
        raw = response.text.strip()
        
        # Cleaner JSON extraction (Removes markdown ```json ... ```)
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.split("```")[0].strip()

        return json.loads(raw)
    except Exception as api_error:
        print(f"Gemini API Error: {api_error}")
        print("Falling back to local quiz generation...")
        
        # Fallback to local quiz generation
        return generate_quiz_locally(text, num_questions)

def generate_quiz_locally(text, num_questions):
    """Generate quiz questions locally without AI API"""
    try:
        # Split text into sentences/paragraphs
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        sentences = [s for s in sentences if len(s) > 20]  # Filter out very short sentences
        
        if len(sentences) < num_questions:
            # If not enough sentences, create questions from key concepts
            sentences = extract_key_concepts(text)
        
        questions = []
        for i in range(min(num_questions, len(sentences))):
            sentence = sentences[i]
            question = create_question_from_sentence(sentence, i)
            if question:
                questions.append(question)
        
        # If still not enough questions, add generic ones
        while len(questions) < num_questions:
            questions.append(create_generic_question(len(questions)))
        
        return questions[:num_questions]
    
    except Exception as e:
        print(f"Local generation error: {e}")
        return []

def extract_key_concepts(text):
    """Extract key concepts from text"""
    # Simple keyword extraction
    words = text.lower().split()
    # Filter out common words
    stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with', 'to', 'for', 'of', 'as', 'by', 'that', 'this', 'it', 'from', 'are', 'be'}
    key_words = [word for word in words if len(word) > 4 and word not in stop_words]
    
    # Return unique words as "concepts"
    concepts = list(set(key_words))[:10]  # Take first 10 unique words
    
    # Create sentences from concepts
    concept_sentences = []
    for concept in concepts:
        concept_sentences = [s for s in text.split('.') if concept.lower() in s.lower()]
        if concept_sentences:
            concept_sentences.append(concept_sentences[0])
    
    return concept_sentences if concept_sentences else [f"The concept of {concept} is important" for concept in concepts[:5]]

def create_question_from_sentence(sentence, index):
    """Create a question from a sentence"""
    if not sentence or len(sentence) < 20:
        return None
    
    # Simple template-based question generation
    templates = [
        {
            "question": f"What is the main topic of this statement: {sentence}?",
            "options": [sentence[:20], "Related topic", "Different subject", "Not mentioned"],
            "correct_answer": 0,
            "explanation": f"The statement discusses {sentence[:30]}..."
        },
        {
            "question": f"According to the text: {sentence[:50]}...",
            "options": ["True", "False", "Partially true", "Cannot determine"],
            "correct_answer": 0,
            "explanation": f"The text states: {sentence[:40]}..."
        },
        {
            "question": f"Which of the following best describes: {sentence[:40]}?",
            "options": [sentence[:30], "Something similar", "Something different", "None of the above"],
            "correct_answer": 0,
            "explanation": f"The description matches: {sentence[:30]}..."
        }
    ]
    
    return templates[index % len(templates)]

def create_generic_question(index):
    """Create a generic question"""
    generic_questions = [
        {
            "question": "What is the main purpose of this document?",
            "options": ["To inform", "To entertain", "To persuade", "To advertise"],
            "correct_answer": 0,
            "explanation": "The document appears to be informational in nature."
        },
        {
            "question": "Which of the following is a key concept in this material?",
            "options": ["Important concept", "Minor detail", "Unrelated topic", "Not covered"],
            "correct_answer": 0,
            "explanation": "This concept is fundamental to understanding the material."
        },
        {
            "question": "What would be the best way to study this content?",
            "options": ["Read carefully", "Skim quickly", "Memorize everything", "Ignore details"],
            "correct_answer": 0,
            "explanation": "Careful reading helps with comprehension and retention."
        },
        {
            "question": "How should you approach questions about this material?",
            "options": ["Confidently", "Cautiously", "Quickly", "Slowly"],
            "correct_answer": 0,
            "explanation": "A confident but careful approach is usually best."
        }
    ]
    
    return generic_questions[index % len(generic_questions)]

# ==============================
# LOGIN REQUIRED DECORATOR
# ==============================

def login_required(role=None):
    def decorator(f):
        def wrapper(*args, **kwargs):

            if "user_id" not in session:
                return redirect("/login")

            if role and session.get("role") != role:
                return redirect("/login")

            return f(*args, **kwargs)

        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

# 2. FIX ATTEND_QUIZ DATA HANDLING
@app.route("/attend_quiz", methods=["GET", "POST"])
@login_required("student")
def attend_quiz():
    if request.method == "GET":
        return render_template("join_quize.html")

    # This handles both Form data and JSON data
    data = request.form if request.form else request.get_json()
    quiz_code = data.get("quiz_code", "").strip().upper()
    
    print(f"DEBUG: Quiz code received: '{quiz_code}'")
    print(f"DEBUG: Request data: {data}")
    
    if not quiz_code:
        print("DEBUG: No quiz code provided")
        return jsonify({"success": False, "message": "Quiz code is required"})

    print(f"DEBUG: Looking for quiz code: '{quiz_code}'")
    code_record = quiz_codes_collection.find_one({"quiz_code": quiz_code, "is_active": True})
    print(f"DEBUG: Code record found: {code_record}")
    
    if not code_record:
        print(f"DEBUG: No active quiz found for code: '{quiz_code}'")
        return jsonify({"success": False, "message": "Invalid or expired quiz code"})

    quiz_id = code_record["quiz_id"]
    print(f"DEBUG: Looking for quiz with ID: '{quiz_id}'")
    quiz = quiz_collection.find_one({"_id": ObjectId(quiz_id)})
    print(f"DEBUG: Quiz found: {quiz is not None}")
    
    if not quiz:
        print(f"DEBUG: Quiz not found for ID: '{quiz_id}'")
        return jsonify({"success": False, "message": "Quiz content not found"})

    # Create the attempt
    attempt_id = str(uuid.uuid4())
    print(f"DEBUG: Creating attempt with ID: '{attempt_id}'")
    
    try:
        quiz_attempts_collection.insert_one({
            "attempt_id": attempt_id,
            "student_id": session["user_id"],
            "quiz_id": str(quiz["_id"]),
            "started_at": datetime.now(),
            "status": "in_progress"
        })
        print(f"DEBUG: Attempt created successfully")
        return jsonify({"success": True, "attempt_id": attempt_id})
    except Exception as e:
        print(f"DEBUG: Error creating attempt: {e}")
        return jsonify({"success": False, "message": "Failed to create quiz attempt"})

# ==============================
# HOME
# ==============================

@app.route("/")
def home():
    return render_template("modern_home.html")


# ==============================
# REGISTER
# ==============================

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        if users_collection.find_one({"email":email}):

            return jsonify({"success":False,"message":"Email exists"})

        users_collection.insert_one({

            "name":name,
            "email":email,
            "password":password,
            "role":role,
            "created_at":datetime.now()

        })

        return jsonify({"success":True,"redirect":"/login"})

    return render_template("modern_register.html")


# ==============================
# LOGIN
# ==============================

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email=request.form["email"]
        password=request.form["password"]

        user=users_collection.find_one({"email":email})

        if user and user["password"]==password:

            session["user_id"]=str(user["_id"])
            session["role"]=user["role"]
            session["name"]=user["name"]

            if user["role"]=="teacher":
                return jsonify({"success":True,"redirect":"/teacher"})

            if user["role"]=="student":
                return jsonify({"success":True,"redirect":"/student"})

        return jsonify({"success":False,"message":"Invalid login"})

    return render_template("modern_login.html")


# ==============================
# LOGOUT
# ==============================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ==============================
# TEACHER DASHBOARD
# ==============================

@app.route("/teacher")
@login_required("teacher")
def teacher():

    quizzes=list(quiz_collection.find({"teacher_id":session["user_id"]}))

    return render_template("teacher_dashboard.html",quizzes=quizzes)

# CREATE QUIZ
# ==============================

@app.route("/create_quiz",methods=["GET","POST"])
@login_required("teacher")
def create_quiz():
    if request.method=="POST":
        try:
            title=request.form["title"]
            subject=request.form["subject"]
            num_questions=int(request.form["num_questions"])
            duration=int(request.form["duration_minutes"])
            file=request.files["file"]
            
            if not file or not allowed_file(file.filename):
                return jsonify({"success":False,"message":"Invalid file"})
            
            filename=str(uuid.uuid4())+"_"+file.filename
            filepath=os.path.join(UPLOAD_FOLDER,filename)
            
            # Save file
            file.save(filepath)
            
            # Extract text and generate questions
            try:
                text=extract_text(filepath)
                if not text or text.strip() == "":
                    return jsonify({"success":False,"message":"Could not extract text from file"})
                
                questions=generate_quiz_from_text(text,num_questions)
                if not questions:
                    return jsonify({"success":False,"message":"AI failed to generate questions from the provided text"})
                
            except Exception as e:
                print(f"Text extraction error: {e}")
                return jsonify({"success":False,"message":"Error processing file content"})
            
            # Clean up uploaded file
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"File cleanup error: {e}")
            
            quiz_code=str(uuid.uuid4()).replace("-","")[:6].upper()
            quiz_data={
                "title":title,
                "subject":subject,
                "questions":questions,
                "duration_minutes":duration,
                "teacher_id":session["user_id"],
                "quiz_code":quiz_code,
                "created_at":datetime.now(),
                "status":"active"
            }
            
            result=quiz_collection.insert_one(quiz_data)
            quiz_codes_collection.insert_one({
                "quiz_id":str(result.inserted_id),
                "quiz_code":quiz_code,
                "created_at":datetime.now(),
                "expires_at":datetime.now()+timedelta(days=30),
                "is_active":True
            })
            
            return jsonify({"success":True,"quiz_code":quiz_code})
            
        except Exception as e:
            print(f"Quiz creation error: {e}")
            return jsonify({"success":False,"message":"An error occurred while creating the quiz. Please try again."})
            
    return render_template("create_quiz.html")


# ==============================
# STUDENT DASHBOARD
# ==============================

@app.route("/student")
@login_required("student")
def student():

    attempts=list(quiz_attempts_collection.find({"student_id":session["user_id"]}))

    return render_template("student_dashboard.html",attempts=attempts)

# TAKE QUIZ
# ==============================

@app.route("/take_quiz/<attempt_id>")
@login_required("student")
def take_quiz(attempt_id):
    print(f"DEBUG: take_quiz called with attempt_id: {attempt_id}")
    
    attempt=quiz_attempts_collection.find_one({"attempt_id":attempt_id})
    print(f"DEBUG: Attempt found: {attempt}")
    
    if not attempt:
        print("DEBUG: No attempt found")
        return redirect("/student")
    
    quiz=quiz_collection.find_one({"_id":ObjectId(attempt["quiz_id"])})
    print(f"DEBUG: Quiz found: {quiz}")
    
    if not quiz:
        print("DEBUG: No quiz found")
        return redirect("/student")
    
    # Debug quiz questions structure
    questions = quiz.get("questions", [])
    print(f"DEBUG: Questions count: {len(questions)}")
    for i, q in enumerate(questions):
        print(f"DEBUG: Question {i}: {q}")
        if 'correct_answer' not in q:
            print(f"DEBUG: Question {i} missing correct_answer field")
            # Try alternative field names
            if 'answer' in q:
                q['correct_answer'] = q['answer']
                print(f"DEBUG: Converted 'answer' to 'correct_answer'")
            elif 'correct' in q:
                q['correct_answer'] = q['correct']
                print(f"DEBUG: Converted 'correct' to 'correct_answer'")
    
    # Ensure all required fields are present
    quiz_data = {
        "_id": str(quiz["_id"]),
        "title": quiz.get("title", "Untitled Quiz"),
        "subject": quiz.get("subject", "General"),
        "duration_minutes": quiz.get("duration_minutes", 30),
        "questions": questions,
        "quiz_code": quiz.get("quiz_code", "UNKNOWN"),
        "attempt_id": attempt_id
    }
    
    print(f"DEBUG: Passing quiz data to template: {quiz_data}")
    return render_template("take_quize.html", quiz=quiz_data, attempt=attempt)


# ==============================
# SUBMIT QUIZ
# ==============================

@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    attempt_id = request.form.get("attempt_id")
    quiz_id = request.form.get("quiz_id")
    
    quiz = quiz_collection.find_one({"_id": ObjectId(quiz_id)})
    questions = quiz.get("questions", [])
    
    correct_count = 0
    total_questions = len(questions)
    
    for i, q in enumerate(questions):
        user_answer = request.form.get(f"q{i}") # Matches name="q{{ loop.index0 }}"
        if user_answer is not None and int(user_answer) == q["correct_answer"]:
            correct_count += 1
            
    percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0
    
    # Update the attempt record
    quiz_attempts_collection.update_one(
        {"attempt_id": attempt_id},
        {"$set": {
            "status": "completed",
            "correct_answers": correct_count,
            "total_questions": total_questions,
            "percentage": percentage,
            "completed_at": datetime.now()
        }}
    )
    
    # Calculate student's rank in leaderboard
    rank = 0
    try:
        # Get all completed attempts for this quiz, sorted by percentage
        all_attempts = list(quiz_attempts_collection.find({
            "quiz_id": quiz_id,
            "status": "completed"
        }).sort("percentage", -1))
        
        # Find current student's rank
        for index, attempt in enumerate(all_attempts):
            if attempt["attempt_id"] == attempt_id:
                rank = index + 1
                break
    except Exception as e:
        print(f"Rank calculation error: {e}")
        rank = 0
    
    return jsonify({"success": True, "result_id": attempt_id, "rank": rank})

# ==============================
# QUIZ RESULTS
# ==============================

@app.route("/quiz_results/<attempt_id>")
@login_required("student")
def quiz_results(attempt_id):
    # Get the completed attempt
    attempt = quiz_attempts_collection.find_one({"attempt_id": attempt_id})
    
    if not attempt or attempt.get("status") != "completed":
        return redirect("/student")
    
    # Get quiz details
    quiz = quiz_collection.find_one({"_id": ObjectId(attempt["quiz_id"])})
    
    if not quiz:
        return redirect("/student")
    
    # Calculate student's rank
    rank = 0
    try:
        # Get all completed attempts for this quiz, sorted by percentage
        all_attempts = list(quiz_attempts_collection.find({
            "quiz_id": attempt["quiz_id"],
            "status": "completed"
        }).sort("percentage", -1))
        
        # Find current student's rank
        for index, ranked_attempt in enumerate(all_attempts):
            if ranked_attempt["attempt_id"] == attempt_id:
                rank = index + 1
                break
    except Exception as e:
        print(f"Rank calculation error: {e}")
        rank = 0
    
    # Prepare score data
    score_data = {
        "percentage": attempt.get("percentage", 0),
        "correct_answers": attempt.get("correct_answers", 0),
        "total_questions": attempt.get("total_questions", 0),
        "obtained_marks": attempt.get("correct_answers", 0),
        "total_marks": attempt.get("total_questions", 0),
        "rank": rank
    }
    
    return render_template("quiz_results.html", 
                      score_data=score_data, 
                      quiz=quiz, 
                      attempt=attempt)


# ==============================
# ACTIVITY REPORTING
# ==============================

@app.route("/report_activity", methods=["POST"])
def report_activity():
    data = request.json
    print("Activity Log:", data)
    return jsonify({"success": True})

@app.route("/heartbeat", methods=["POST"])
def heartbeat():
    return jsonify({"alive": True})

# ==============================
# LEADERBOARD ROUTES
# ==============================

@app.route("/leaderboard")
@login_required()
def leaderboard_general():
    # Show all available quiz leaderboards
    quizzes = list(quiz_collection.find({"status": "active"}))
    
    # Get recent completed attempts for each quiz
    leaderboard_data = []
    for quiz in quizzes:
        quiz_id = str(quiz["_id"])
        attempts_cursor = quiz_attempts_collection.find({
            "quiz_id": quiz_id,
            "status": "completed"
        }).sort("percentage", -1).limit(10)  # Top 10 per quiz
        
        attempts = list(attempts_cursor)
        
        # Enrich with student names
        enriched_attempts = []
        for index, attempt in enumerate(attempts):
            student = users_collection.find_one({"_id": ObjectId(attempt["student_id"])})
            enriched_attempts.append({
                "rank": index + 1,
                "student_name": student["name"] if student else "Unknown Student",
                "percentage": attempt.get("percentage", 0),
                "completed_at": attempt.get("completed_at")
            })
        
        leaderboard_data.append({
            "quiz": quiz,
            "top_performers": enriched_attempts,
            "total_participants": len(attempts)
        })
    
    return render_template(
        "leaderboard_general.html", 
        leaderboards=leaderboard_data,
        total_quizzes=len(quizzes)
    )

@app.route("/leaderboard/<quiz_id>")
@login_required()
def leaderboard(quiz_id):
    # 1. Fetch all completed attempts for this quiz, sorted by percentage
    attempts_cursor = quiz_attempts_collection.find({
        "quiz_id": quiz_id,
        "status": "completed"
    }).sort("percentage", -1)

    attempts = list(attempts_cursor)
    
    # 2. Enrich attempt data with student names from users collection
    enriched_attempts = []
    top_performer = None
    current_student_rank = None

    for index, attempt in enumerate(attempts):
        student = users_collection.find_one({"_id": ObjectId(attempt["student_id"])})
        
        attempt_data = {
            "rank": index + 1,
            "attempt_id": attempt.get("attempt_id"),
            "student_name": student["name"] if student else "Unknown Student",
            "student_email": student["email"] if student else "N/A",
            "percentage": attempt.get("percentage", 0),
            "correct_answers": attempt.get("correct_answers", 0),
            "total_questions": attempt.get("total_questions", 0),
            "completed_at": attempt.get("completed_at")
        }
        
        enriched_attempts.append(attempt_data)
        
        # Set top performer (rank 1)
        if index == 0:
            top_performer = attempt_data
            
        # Check if this is current logged-in user's rank
        if attempt["student_id"] == session.get("user_id"):
            current_student_rank = index + 1

    return render_template(
        "leaderboard.html", 
        attempts=enriched_attempts,
        top_performer=top_performer,
        total_participants=len(enriched_attempts),
        current_student_rank=current_student_rank,
        quiz_id=quiz_id
    )

# ==============================
# API FOR REAL-TIME UPDATES
# ==============================

@app.route("/api/leaderboard/<quiz_id>")
def api_leaderboard(quiz_id):
    count = quiz_attempts_collection.count_documents({"quiz_id": quiz_id, "status": "completed"})
    return jsonify({"success": True, "total_participants": count})

# ==============================
# STUDENT PROGRESS TRACKING
# ==============================

@app.route("/student_progress")
@login_required("student")
def student_progress():
    attempts = list(quiz_attempts_collection.find({"student_id": session["user_id"]}))
    
    # Calculate statistics
    completed_attempts = [a for a in attempts if a.get("status") == "completed"]
    in_progress_attempts = [a for a in attempts if a.get("status") == "in_progress"]
    expired_attempts = [a for a in attempts if a.get("status") == "expired"]
    
    # Get quiz details for each attempt
    progress_data = []
    for attempt in attempts:
        quiz = quiz_collection.find_one({"_id": ObjectId(attempt["quiz_id"])})
        progress_data.append({
            "attempt": attempt,
            "quiz_title": quiz.get("title", "Unknown Quiz") if quiz else "Unknown Quiz",
            "quiz_subject": quiz.get("subject", "General") if quiz else "General",
            "total_questions": len(quiz.get("questions", [])) if quiz else 0
        })
    
    # Calculate overall statistics
    total_score = sum(a.get("percentage", 0) for a in completed_attempts)
    best_score = max(a.get("percentage", 0) for a in completed_attempts) if completed_attempts else 0
    avg_score = total_score / len(completed_attempts) if completed_attempts else 0
    
    # Calculate total questions attempted
    total_questions_attempted = 0
    for attempt in attempts:
        quiz = quiz_collection.find_one({"_id": ObjectId(attempt["quiz_id"])})
        if quiz and "questions" in quiz:
            total_questions_attempted += len(quiz["questions"])
    
    return jsonify({
        "success": True,
        "statistics": {
            "total_attempts": len(attempts),
            "completed": len(completed_attempts),
            "in_progress": len(in_progress_attempts),
            "expired": len(expired_attempts),
            "average_score": round(avg_score, 1),
            "best_score": round(best_score, 1),
            "total_questions_attempted": total_questions_attempted
        },
        "progress_data": progress_data
    })

# ==============================
# RUN SERVER
# ==============================

if __name__=="__main__":

    print("AI Quiz Platform Running")
    print("http://localhost:5000")

    app.run(debug=True)