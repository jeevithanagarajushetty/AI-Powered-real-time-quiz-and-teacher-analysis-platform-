"""
Quiz Management Module
Handles quiz code generation, validation, and quiz operations
"""

import uuid
import random
import string
from datetime import datetime, timedelta
from config import quiz_collection, quiz_codes_collection, quiz_attempts_collection
from modules.database_models import QuizModels, QuizAttemptModels

class QuizManager:
    """Manages quiz creation, codes, and validation"""
    
    @staticmethod
    def generate_unique_quiz_code():
        """Generate a unique 6-character quiz code"""
        max_attempts = 100
        attempts = 0
        
        while attempts < max_attempts:
            # Generate 6-character code with mix of uppercase letters and numbers
            code = ''.join(random.choices(
                string.ascii_uppercase + string.digits, 
                k=6
            ))
            
            # Check if code already exists
            existing = quiz_codes_collection.find_one({"quiz_code": code})
            if not existing:
                return code
            
            attempts += 1
        
        # Fallback to UUID-based code if all attempts fail
        return str(uuid.uuid4())[:8].upper()
    
    @staticmethod
    def create_quiz_with_code(quiz_data):
        """Create a new quiz with unique code"""
        try:
            # Generate unique quiz code
            quiz_code = QuizManager.generate_unique_quiz_code()
            
            # Create quiz document
            quiz = QuizModels.create_quiz_schema()
            quiz.update({
                "quiz_code": quiz_code,
                "title": quiz_data.get("title", ""),
                "subject": quiz_data.get("subject", ""),
                "teacher_id": quiz_data.get("teacher_id", ""),
                "teacher_name": quiz_data.get("teacher_name", ""),
                "difficulty": quiz_data.get("difficulty", "medium"),
                "duration_minutes": int(quiz_data.get("duration_minutes", 30)),
                "total_marks": int(quiz_data.get("total_marks", 10)),
                "questions": quiz_data.get("questions", []),
                "status": "active"
            })
            
            # Insert quiz into database
            quiz_collection.insert_one(quiz)
            
            # Create quiz code record
            quiz_code_record = {
                "quiz_code": quiz_code,
                "quiz_id": quiz["quiz_id"],
                "teacher_id": quiz_data.get("teacher_id", ""),
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(days=30),  # Code expires in 30 days
                "is_active": True,
                "max_attempts": quiz_data.get("max_attempts", 1),  # Per student
                "allowed_students": quiz_data.get("allowed_students", []),  # Optional: restrict to specific students
                "settings": {
                    "show_correct_answers": quiz_data.get("show_correct_answers", False),
                    "allow_review": quiz_data.get("allow_review", False),
                    "randomize_questions": quiz_data.get("randomize_questions", True),
                    "auto_submit_on_timeout": quiz_data.get("auto_submit_on_timeout", True),
                    "prevent_tab_switch": quiz_data.get("prevent_tab_switch", True),
                    "max_warnings": int(quiz_data.get("max_warnings", 3))
                }
            }
            
            quiz_codes_collection.insert_one(quiz_code_record)
            
            return {
                "success": True,
                "quiz_id": quiz["quiz_id"],
                "quiz_code": quiz_code,
                "message": "Quiz created successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create quiz"
            }
    
    @staticmethod
    def validate_quiz_code(quiz_code):
        """Validate if quiz code exists and is active"""
        try:
            code_record = quiz_codes_collection.find_one({
                "quiz_code": quiz_code.upper(),
                "is_active": True
            })
            
            if not code_record:
                return {
                    "valid": False,
                    "message": "Invalid quiz code"
                }
            
            # Check if code has expired
            if code_record.get("expires_at") and datetime.now() > code_record["expires_at"]:
                return {
                    "valid": False,
                    "message": "Quiz code has expired"
                }
            
            # Get quiz details
            quiz = quiz_collection.find_one({"quiz_id": code_record["quiz_id"]})
            if not quiz:
                return {
                    "valid": False,
                    "message": "Quiz not found"
                }
            
            return {
                "valid": True,
                "quiz": quiz,
                "quiz_code_record": code_record,
                "message": "Quiz code is valid"
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "message": "Error validating quiz code"
            }
    
    @staticmethod
    def get_quiz_by_code(quiz_code):
        """Get quiz details using quiz code"""
        validation = QuizManager.validate_quiz_code(quiz_code)
        
        if validation["valid"]:
            return validation["quiz"]
        else:
            return None
    
    @staticmethod
    def can_student_attempt_quiz(student_id, quiz_code):
        """Check if student can attempt the quiz"""
        try:
            # Validate quiz code first
            validation = QuizManager.validate_quiz_code(quiz_code)
            if not validation["valid"]:
                return {
                    "can_attempt": False,
                    "message": validation["message"]
                }
            
            quiz_code_record = validation["quiz_code_record"]
            
            # Check if student has already attempted
            existing_attempt = quiz_attempts_collection.find_one({
                "quiz_code": quiz_code.upper(),
                "student_id": student_id,
                "status": {"$in": ["submitted", "auto_submitted"]}
            })
            
            if existing_attempt:
                return {
                    "can_attempt": False,
                    "message": "You have already attempted this quiz",
                    "attempt": existing_attempt
                }
            
            # Check if student is currently attempting
            current_attempt = quiz_attempts_collection.find_one({
                "quiz_code": quiz_code.upper(),
                "student_id": student_id,
                "status": "in_progress"
            })
            
            if current_attempt:
                return {
                    "can_attempt": True,
                    "message": "You have an ongoing attempt",
                    "attempt": current_attempt
                }
            
            # Check if student is in allowed list (if restricted)
            allowed_students = quiz_code_record.get("allowed_students", [])
            if allowed_students and student_id not in allowed_students:
                return {
                    "can_attempt": False,
                    "message": "You are not authorized to attempt this quiz"
                }
            
            return {
                "can_attempt": True,
                "message": "You can attempt this quiz"
            }
            
        except Exception as e:
            return {
                "can_attempt": False,
                "error": str(e),
                "message": "Error checking quiz eligibility"
            }
    
    @staticmethod
    def start_quiz_attempt(student_data, quiz_code):
        """Start a new quiz attempt for a student"""
        try:
            # Check if student can attempt
            eligibility = QuizManager.can_student_attempt_quiz(
                student_data["student_id"], 
                quiz_code
            )
            
            if not eligibility["can_attempt"]:
                return {
                    "success": False,
                    "message": eligibility["message"]
                }
            
            # Get quiz details
            quiz = QuizManager.get_quiz_by_code(quiz_code)
            if not quiz:
                return {
                    "success": False,
                    "message": "Quiz not found"
                }
            
            # Create quiz attempt
            attempt = QuizAttemptModels.create_attempt_schema()
            attempt.update({
                "quiz_id": quiz["quiz_id"],
                "quiz_code": quiz_code.upper(),
                "student_id": student_data["student_id"],
                "student_name": student_data["name"],
                "register_number": student_data["register_number"],
                "started_at": datetime.now(),
                "status": "in_progress",
                "total_marks": quiz["total_marks"],
                "warnings": 0
            })
            
            # Insert attempt
            quiz_attempts_collection.insert_one(attempt)
            
            # Prepare questions for student (randomize if needed)
            questions = quiz["questions"].copy()
            if quiz["settings"]["randomize_questions"]:
                random.shuffle(questions)
            
            return {
                "success": True,
                "attempt_id": attempt["attempt_id"],
                "quiz": quiz,
                "questions": questions,
                "started_at": attempt["started_at"],
                "duration_minutes": quiz["duration_minutes"],
                "message": "Quiz started successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to start quiz"
            }
    
    @staticmethod
    def get_active_quizzes_for_teacher(teacher_id):
        """Get all active quizzes for a teacher"""
        try:
            quizzes = list(quiz_collection.find({
                "teacher_id": teacher_id,
                "status": {"$in": ["active", "completed"]}
            }).sort("created_at", -1))
            
            # Convert ObjectId to string for JSON serialization
            for quiz in quizzes:
                quiz["_id"] = str(quiz["_id"])
            
            return {
                "success": True,
                "quizzes": quizzes
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to fetch quizzes"
            }
    
    @staticmethod
    def deactivate_quiz_code(quiz_code):
        """Deactivate a quiz code"""
        try:
            result = quiz_codes_collection.update_one(
                {"quiz_code": quiz_code.upper()},
                {"$set": {"is_active": False, "deactivated_at": datetime.now()}}
            )
            
            if result.modified_count > 0:
                return {
                    "success": True,
                    "message": "Quiz code deactivated successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "Quiz code not found or already inactive"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to deactivate quiz code"
            }
    
    @staticmethod
    def get_quiz_statistics(quiz_id):
        """Get comprehensive statistics for a quiz"""
        try:
            # Get quiz details
            quiz = quiz_collection.find_one({"quiz_id": quiz_id})
            if not quiz:
                return {"success": False, "message": "Quiz not found"}
            
            # Get all attempts
            attempts = list(quiz_attempts_collection.find({
                "quiz_id": quiz_id
            }))
            
            # Calculate statistics
            total_attempts = len(attempts)
            submitted_attempts = len([a for a in attempts if a["status"] in ["submitted", "auto_submitted"]])
            in_progress_attempts = len([a for a in attempts if a["status"] == "in_progress"])
            
            if submitted_attempts > 0:
                scores = [a["score"] for a in attempts if a["status"] in ["submitted", "auto_submitted"]]
                average_score = sum(scores) / len(scores)
                highest_score = max(scores)
                lowest_score = min(scores)
                
                # Calculate pass percentage (assuming 50% is passing)
                pass_count = len([s for s in scores if s >= (quiz["total_marks"] * 0.5)])
                pass_percentage = (pass_count / len(scores)) * 100
            else:
                average_score = 0
                highest_score = 0
                lowest_score = 0
                pass_percentage = 0
            
            # Malactivity statistics
            malactivity_incidents = sum(len(a.get("malactivity_detected", [])) for a in attempts)
            
            return {
                "success": True,
                "statistics": {
                    "quiz_title": quiz["title"],
                    "quiz_code": quiz["quiz_code"],
                    "total_attempts": total_attempts,
                    "submitted_attempts": submitted_attempts,
                    "in_progress_attempts": in_progress_attempts,
                    "completion_rate": (submitted_attempts / total_attempts * 100) if total_attempts > 0 else 0,
                    "average_score": average_score,
                    "highest_score": highest_score,
                    "lowest_score": lowest_score,
                    "pass_percentage": pass_percentage,
                    "malactivity_incidents": malactivity_incidents,
                    "average_time": 0  # TODO: Calculate average time taken
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to fetch quiz statistics"
            }
