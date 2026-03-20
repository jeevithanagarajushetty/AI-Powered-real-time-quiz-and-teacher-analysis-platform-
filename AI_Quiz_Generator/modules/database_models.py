"""
Database Models and Schemas for AI Quiz Platform
"""

from datetime import datetime, timedelta
import uuid
import random
import string

class UserModels:
    """User related database operations"""
    
    @staticmethod
    def create_user_schema():
        return {
            "user_id": str(uuid.uuid4()),
            "name": "",
            "email": "",
            "mobile": "",
            "password": "",
            "role": "",  # student, teacher, admin
            "register_number": "",  # for students
            "created_at": datetime.now(),
            "is_active": True,
            "profile": {
                "department": "",
                "semester": "",
                "section": ""
            }
        }
    
    @staticmethod
    def create_student_schema():
        schema = UserModels.create_user_schema()
        schema.update({
            "role": "student",
            "register_number": "",
            "quiz_history": [],
            "current_quiz": None,
            "warnings": 0,
            "banned_until": None
        })
        return schema
    
    @staticmethod
    def create_teacher_schema():
        schema = UserModels.create_user_schema()
        schema.update({
            "role": "teacher",
            "employee_id": "",
            "department": "",
            "created_quizzes": [],
            "subjects": []
        })
        return schema
    
    @staticmethod
    def create_admin_schema():
        schema = UserModels.create_user_schema()
        schema.update({
            "role": "admin",
            "admin_level": "super",  # super, department, college
            "permissions": ["all"]
        })
        return schema

class QuizModels:
    """Quiz related database operations"""
    
    @staticmethod
    def generate_quiz_code():
        """Generate unique 6-digit quiz code"""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            return code
    
    @staticmethod
    def create_quiz_schema():
        return {
            "quiz_id": str(uuid.uuid4()),
            "quiz_code": "",
            "title": "",
            "subject": "",
            "teacher_id": "",
            "teacher_name": "",
            "difficulty": "",  # easy, medium, hard
            "duration_minutes": 0,
            "total_marks": 0,
            "questions": [],
            "created_at": datetime.now(),
            "scheduled_for": None,
            "status": "draft",  # draft, active, completed
            "settings": {
                "allow_review": False,
                "show_results_immediately": True,
                "randomize_questions": True,
                "auto_submit_on_timeout": True
            }
        }
    
    @staticmethod
    def create_question_schema():
        return {
            "question_id": str(uuid.uuid4()),
            "question_text": "",
            "question_type": "mcq",  # mcq, true_false, short_answer
            "options": [],
            "correct_answer": "",
            "marks": 1,
            "explanation": "",
            "difficulty": "medium"
        }

class QuizAttemptModels:
    """Quiz attempt tracking models"""
    
    @staticmethod
    def create_attempt_schema():
        return {
            "attempt_id": str(uuid.uuid4()),
            "quiz_id": "",
            "quiz_code": "",
            "student_id": "",
            "student_name": "",
            "register_number": "",
            "started_at": None,
            "submitted_at": None,
            "status": "not_started",  # not_started, in_progress, submitted, auto_submitted, banned
            "answers": {},
            "score": 0,
            "total_marks": 0,
            "percentage": 0,
            "warnings": 0,
            "malactivity_detected": [],
            "time_taken_seconds": 0,
            "browser_events": []
        }
    
    @staticmethod
    def create_malactivity_event():
        return {
            "timestamp": datetime.now(),
            "event_type": "",  # tab_switch, window_focus_lost, copy_paste, right_click
            "warning_count": 0,
            "action_taken": ""  # warning, auto_submit, ban
        }

class ResultModels:
    """Results and ranking models"""
    
    @staticmethod
    def create_result_schema():
        return {
            "result_id": str(uuid.uuid4()),
            "quiz_id": "",
            "quiz_code": "",
            "quiz_title": "",
            "subject": "",
            "conducted_at": datetime.now(),
            "total_participants": 0,
            "rankings": [],
            "statistics": {
                "average_score": 0,
                "highest_score": 0,
                "lowest_score": 0,
                "pass_percentage": 0
            },
            "top_performer": {
                "name": "",
                "register_number": "",
                "score": 0,
                "percentage": 0
            }
        }
    
    @staticmethod
    def create_ranking_schema():
        return {
            "rank": 0,
            "student_id": "",
            "register_number": "",
            "name": "",
            "score": 0,
            "percentage": 0,
            "time_taken": "",
            "submitted_at": None
        }

class AnalyticsModels:
    """Analytics and reporting models"""
    
    @staticmethod
    def create_analytics_schema():
        return {
            "analytics_id": str(uuid.uuid4()),
            "type": "",  # quiz_performance, student_progress, teacher_effectiveness
            "reference_id": "",  # quiz_id, student_id, teacher_id
            "data": {},
            "generated_at": datetime.now(),
            "period": {
                "start": None,
                "end": None
            }
        }
    
    @staticmethod
    def create_quiz_analytics():
        return {
            "quiz_id": "",
            "total_attempts": 0,
            "completion_rate": 0,
            "average_score": 0,
            "average_time": 0,
            "question_analysis": [],
            "difficulty_distribution": {
                "easy": 0,
                "medium": 0,
                "hard": 0
            },
            "malactivity_incidents": 0
        }

class SubjectModels:
    """Subject management models"""
    
    @staticmethod
    def create_subject_schema():
        return {
            "subject_id": str(uuid.uuid4()),
            "name": "",
            "code": "",
            "department": "",
            "description": "",
            "teachers": [],
            "total_quizzes": 0,
            "created_at": datetime.now(),
            "is_active": True
        }
