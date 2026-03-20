"""
Analytics Engine Module
Comprehensive analytics and reporting for the AI Quiz Platform
"""

from datetime import datetime, timedelta
from config import (
    users_collection, quiz_collection, quiz_attempts_collection, 
    quiz_codes_collection, results_collection
)
from modules.database_models import AnalyticsModels
import json

class AnalyticsEngine:
    """Main analytics engine for generating insights and reports"""
    
    @staticmethod
    def generate_platform_analytics(period='monthly'):
        """Generate comprehensive platform analytics"""
        try:
            # Calculate date range
            end_date = datetime.now()
            if period == 'daily':
                start_date = end_date - timedelta(days=1)
            elif period == 'weekly':
                start_date = end_date - timedelta(weeks=1)
            elif period == 'monthly':
                start_date = end_date - timedelta(days=30)
            elif period == 'yearly':
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)
            
            # User analytics
            user_stats = AnalyticsEngine._get_user_statistics(start_date, end_date)
            
            # Quiz analytics
            quiz_stats = AnalyticsEngine._get_quiz_statistics(start_date, end_date)
            
            # Performance analytics
            performance_stats = AnalyticsEngine._get_performance_statistics(start_date, end_date)
            
            # Engagement analytics
            engagement_stats = AnalyticsEngine._get_engagement_statistics(start_date, end_date)
            
            # Malactivity analytics
            malactivity_stats = AnalyticsEngine._get_malactivity_statistics(start_date, end_date)
            
            analytics_data = {
                "period": period,
                "date_range": {
                    "start": start_date,
                    "end": end_date
                },
                "generated_at": datetime.now(),
                "user_analytics": user_stats,
                "quiz_analytics": quiz_stats,
                "performance_analytics": performance_stats,
                "engagement_analytics": engagement_stats,
                "malactivity_analytics": malactivity_stats
            }
            
            return {
                "success": True,
                "analytics": analytics_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate platform analytics"
            }
    
    @staticmethod
    def _get_user_statistics(start_date, end_date):
        """Get user-related statistics"""
        # Total users
        total_users = users_collection.count_documents({
            "created_at": {"$gte": start_date, "$lte": end_date}
        })
        
        # Users by role
        users_by_role = {}
        for role in ['student', 'teacher', 'admin']:
            count = users_collection.count_documents({
                "role": role,
                "created_at": {"$gte": start_date, "$lte": end_date}
            })
            users_by_role[role] = count
        
        # Active users (users who attempted quizzes)
        active_users = quiz_attempts_collection.distinct(
            "student_id",
            {"started_at": {"$gte": start_date, "$lte": end_date}}
        )
        
        # User registration trend
        registration_trend = AnalyticsEngine._get_registration_trend(start_date, end_date)
        
        return {
            "total_new_users": total_users,
            "users_by_role": users_by_role,
            "active_users_count": len(active_users),
            "user_activity_rate": (len(active_users) / total_users * 100) if total_users > 0 else 0,
            "registration_trend": registration_trend
        }
    
    @staticmethod
    def _get_quiz_statistics(start_date, end_date):
        """Get quiz-related statistics"""
        # Total quizzes created
        total_quizzes = quiz_collection.count_documents({
            "created_at": {"$gte": start_date, "$lte": end_date}
        })
        
        # Quizzes by difficulty
        quizzes_by_difficulty = {}
        for difficulty in ['easy', 'medium', 'hard']:
            count = quiz_collection.count_documents({
                "difficulty": difficulty,
                "created_at": {"$gte": start_date, "$lte": end_date}
            })
            quizzes_by_difficulty[difficulty] = count
        
        # Quiz attempts
        total_attempts = quiz_attempts_collection.count_documents({
            "started_at": {"$gte": start_date, "$lte": end_date}
        })
        
        # Completed attempts
        completed_attempts = quiz_attempts_collection.count_documents({
            "started_at": {"$gte": start_date, "$lte": end_date},
            "status": {"$in": ["submitted", "auto_submitted"]}
        })
        
        # Completion rate
        completion_rate = (completed_attempts / total_attempts * 100) if total_attempts > 0 else 0
        
        # Average quiz duration
        completed_quiz_attempts = quiz_attempts_collection.find({
            "started_at": {"$gte": start_date, "$lte": end_date},
            "status": {"$in": ["submitted", "auto_submitted"]}
        })
        
        durations = []
        for attempt in completed_quiz_attempts:
            if attempt.get("time_taken_seconds"):
                durations.append(attempt["time_taken_seconds"])
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "total_quizzes_created": total_quizzes,
            "quizzes_by_difficulty": quizzes_by_difficulty,
            "total_attempts": total_attempts,
            "completed_attempts": completed_attempts,
            "completion_rate": completion_rate,
            "average_duration_seconds": avg_duration,
            "average_duration_formatted": str(timedelta(seconds=int(avg_duration)))
        }
    
    @staticmethod
    def _get_performance_statistics(start_date, end_date):
        """Get performance-related statistics"""
        # Get all completed attempts in the period
        completed_attempts = list(quiz_attempts_collection.find({
            "started_at": {"$gte": start_date, "$lte": end_date},
            "status": {"$in": ["submitted", "auto_submitted"]}
        }))
        
        if not completed_attempts:
            return {
                "average_score": 0,
                "highest_score": 0,
                "lowest_score": 0,
                "pass_rate": 0,
                "score_distribution": {},
                "performance_trend": []
            }
        
        # Calculate scores
        scores = [attempt.get("score", 0) for attempt in completed_attempts]
        percentages = [attempt.get("percentage", 0) for attempt in completed_attempts]
        
        # Basic statistics
        average_score = sum(scores) / len(scores)
        highest_score = max(scores)
        lowest_score = min(scores)
        average_percentage = sum(percentages) / len(percentages)
        
        # Pass rate (assuming 50% is passing)
        pass_count = len([p for p in percentages if p >= 50])
        pass_rate = (pass_count / len(percentages)) * 100
        
        # Score distribution
        score_ranges = {
            "0-20": 0,
            "21-40": 0,
            "41-60": 0,
            "61-80": 0,
            "81-100": 0
        }
        
        for percentage in percentages:
            if percentage <= 20:
                score_ranges["0-20"] += 1
            elif percentage <= 40:
                score_ranges["21-40"] += 1
            elif percentage <= 60:
                score_ranges["41-60"] += 1
            elif percentage <= 80:
                score_ranges["61-80"] += 1
            else:
                score_ranges["81-100"] += 1
        
        # Performance trend over time
        performance_trend = AnalyticsEngine._get_performance_trend(start_date, end_date)
        
        return {
            "average_score": average_score,
            "average_percentage": average_percentage,
            "highest_score": highest_score,
            "lowest_score": lowest_score,
            "pass_rate": pass_rate,
            "total_participants": len(completed_attempts),
            "score_distribution": score_ranges,
            "performance_trend": performance_trend
        }
    
    @staticmethod
    def _get_engagement_statistics(start_date, end_date):
        """Get user engagement statistics"""
        # Daily active users
        daily_active_users = AnalyticsEngine._get_daily_active_users(start_date, end_date)
        
        # Peak activity hours
        peak_hours = AnalyticsEngine._get_peak_activity_hours(start_date, end_date)
        
        # Subject popularity
        subject_popularity = AnalyticsEngine._get_subject_popularity(start_date, end_date)
        
        # Device/platform usage (if available)
        platform_usage = AnalyticsEngine._get_platform_usage(start_date, end_date)
        
        return {
            "daily_active_users": daily_active_users,
            "peak_activity_hours": peak_hours,
            "subject_popularity": subject_popularity,
            "platform_usage": platform_usage
        }
    
    @staticmethod
    def _get_malactivity_statistics(start_date, end_date):
        """Get malactivity and security statistics"""
        # Total malactivity incidents
        attempts_with_incidents = quiz_attempts_collection.find({
            "started_at": {"$gte": start_date, "$lte": end_date},
            "malactivity_detected": {"$exists": True, "$ne": []}
        })
        
        total_incidents = 0
        incident_types = {}
        auto_submissions = 0
        
        for attempt in attempts_with_incidents:
            incidents = attempt.get("malactivity_detected", [])
            total_incidents += len(incidents)
            
            if attempt.get("status") == "auto_submitted":
                auto_submissions += 1
            
            for incident in incidents:
                incident_type = incident.get("event_type", "unknown")
                incident_types[incident_type] = incident_types.get(incident_type, 0) + 1
        
        # Security score (higher is better)
        total_attempts = quiz_attempts_collection.count_documents({
            "started_at": {"$gte": start_date, "$lte": end_date}
        })
        
        incident_rate = (total_incidents / total_attempts * 100) if total_attempts > 0 else 0
        security_score = max(0, 100 - incident_rate)
        
        return {
            "total_incidents": total_incidents,
            "incident_types": incident_types,
            "auto_submissions": auto_submissions,
            "incident_rate": incident_rate,
            "security_score": security_score,
            "total_attempts_monitored": total_attempts
        }
    
    @staticmethod
    def _get_registration_trend(start_date, end_date):
        """Get user registration trend over time"""
        # Group by day
        pipeline = [
            {
                "$match": {
                    "created_at": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$created_at"
                        }
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        result = list(users_collection.aggregate(pipeline))
        return [{"date": item["_id"], "registrations": item["count"]} for item in result]
    
    @staticmethod
    def _get_performance_trend(start_date, end_date):
        """Get performance trend over time"""
        # Group by day
        pipeline = [
            {
                "$match": {
                    "started_at": {"$gte": start_date, "$lte": end_date},
                    "status": {"$in": ["submitted", "auto_submitted"]}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$started_at"
                        }
                    },
                    "avg_score": {"$avg": "$score"},
                    "avg_percentage": {"$avg": "$percentage"},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        result = list(quiz_attempts_collection.aggregate(pipeline))
        return [
            {
                "date": item["_id"],
                "average_score": round(item["avg_score"], 2),
                "average_percentage": round(item["avg_percentage"], 2),
                "participants": item["count"]
            } 
            for item in result
        ]
    
    @staticmethod
    def _get_daily_active_users(start_date, end_date):
        """Get daily active users"""
        pipeline = [
            {
                "$match": {
                    "started_at": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$started_at"
                        }
                    },
                    "unique_users": {"$addToSet": "$student_id"}
                }
            },
            {
                "$project": {
                    "date": "$_id",
                    "active_users": {"$size": "$unique_users"}
                }
            },
            {"$sort": {"date": 1}}
        ]
        
        result = list(quiz_attempts_collection.aggregate(pipeline))
        return [{"date": item["date"], "active_users": item["active_users"]} for item in result]
    
    @staticmethod
    def _get_peak_activity_hours(start_date, end_date):
        """Get peak activity hours"""
        pipeline = [
            {
                "$match": {
                    "started_at": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$hour": "$started_at"
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ]
        
        result = list(quiz_attempts_collection.aggregate(pipeline))
        return [{"hour": item["_id"], "attempts": item["count"]} for item in result]
    
    @staticmethod
    def _get_subject_popularity(start_date, end_date):
        """Get subject popularity statistics"""
        pipeline = [
            {
                "$match": {
                    "started_at": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$lookup": {
                    "from": "quiz",
                    "localField": "quiz_id",
                    "foreignField": "quiz_id",
                    "as": "quiz_info"
                }
            },
            {"$unwind": "$quiz_info"},
            {
                "$group": {
                    "_id": "$quiz_info.subject",
                    "attempts": {"$sum": 1},
                    "unique_students": {"$addToSet": "$student_id"}
                }
            },
            {
                "$project": {
                    "subject": "$_id",
                    "total_attempts": "$attempts",
                    "unique_students": {"$size": "$unique_students"}
                }
            },
            {"$sort": {"total_attempts": -1}}
        ]
        
        result = list(quiz_attempts_collection.aggregate(pipeline))
        return result
    
    @staticmethod
    def _get_platform_usage(start_date, end_date):
        """Get platform usage statistics"""
        # This would be enhanced with actual device/browser tracking
        # For now, return basic usage metrics
        total_attempts = quiz_attempts_collection.count_documents({
            "started_at": {"$gte": start_date, "$lte": end_date}
        })
        
        return {
            "total_sessions": total_attempts,
            "avg_session_duration": "25 minutes",  # Placeholder
            "bounce_rate": "15%",  # Placeholder
            "return_user_rate": "78%"  # Placeholder
        }
    
    @staticmethod
    def generate_teacher_analytics(teacher_id, period='monthly'):
        """Generate analytics specific to a teacher"""
        try:
            # Calculate date range
            end_date = datetime.now()
            if period == 'daily':
                start_date = end_date - timedelta(days=1)
            elif period == 'weekly':
                start_date = end_date - timedelta(weeks=1)
            elif period == 'monthly':
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Get teacher's quizzes
            teacher_quizzes = list(quiz_collection.find({
                "teacher_id": teacher_id,
                "created_at": {"$gte": start_date, "$lte": end_date}
            }))
            
            quiz_ids = [quiz["quiz_id"] for quiz in teacher_quizzes]
            
            # Get attempts for teacher's quizzes
            attempts = list(quiz_attempts_collection.find({
                "quiz_id": {"$in": quiz_ids},
                "started_at": {"$gte": start_date, "$lte": end_date}
            }))
            
            completed_attempts = [a for a in attempts if a["status"] in ["submitted", "auto_submitted"]]
            
            # Calculate metrics
            total_quizzes = len(teacher_quizzes)
            total_attempts = len(attempts)
            total_completed = len(completed_attempts)
            
            if completed_attempts:
                scores = [a.get("score", 0) for a in completed_attempts]
                percentages = [a.get("percentage", 0) for a in completed_attempts]
                avg_score = sum(scores) / len(scores)
                avg_percentage = sum(percentages) / len(percentages)
                pass_count = len([p for p in percentages if p >= 50])
                pass_rate = (pass_count / len(percentages)) * 100
            else:
                avg_score = 0
                avg_percentage = 0
                pass_rate = 0
            
            # Subject-wise performance
            subject_performance = {}
            for quiz in teacher_quizzes:
                subject = quiz.get("subject", "Unknown")
                quiz_attempts = [a for a in completed_attempts if a["quiz_id"] == quiz["quiz_id"]]
                
                if quiz_attempts:
                    quiz_percentages = [a.get("percentage", 0) for a in quiz_attempts]
                    subject_performance[subject] = {
                        "attempts": len(quiz_attempts),
                        "average_percentage": sum(quiz_percentages) / len(quiz_percentages)
                    }
            
            return {
                "success": True,
                "analytics": {
                    "period": period,
                    "total_quizzes_created": total_quizzes,
                    "total_attempts": total_attempts,
                    "completed_attempts": total_completed,
                    "completion_rate": (total_completed / total_attempts * 100) if total_attempts > 0 else 0,
                    "average_score": avg_score,
                    "average_percentage": avg_percentage,
                    "pass_rate": pass_rate,
                    "subject_performance": subject_performance
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate teacher analytics"
            }
    
    @staticmethod
    def generate_student_analytics(student_id, period='monthly'):
        """Generate analytics specific to a student"""
        try:
            # Calculate date range
            end_date = datetime.now()
            if period == 'daily':
                start_date = end_date - timedelta(days=1)
            elif period == 'weekly':
                start_date = end_date - timedelta(weeks=1)
            elif period == 'monthly':
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Get student's attempts
            attempts = list(quiz_attempts_collection.find({
                "student_id": student_id,
                "started_at": {"$gte": start_date, "$lte": end_date}
            }))
            
            completed_attempts = [a for a in attempts if a["status"] in ["submitted", "auto_submitted"]]
            
            # Calculate metrics
            total_attempts = len(attempts)
            total_completed = len(completed_attempts)
            
            if completed_attempts:
                scores = [a.get("score", 0) for a in completed_attempts]
                percentages = [a.get("percentage", 0) for a in completed_attempts]
                avg_score = sum(scores) / len(scores)
                avg_percentage = sum(percentages) / len(percentages)
                highest_score = max(scores)
                lowest_score = min(scores)
                
                # Subject-wise performance
                subject_performance = {}
                for attempt in completed_attempts:
                    quiz = quiz_collection.find_one({"quiz_id": attempt["quiz_id"]})
                    if quiz:
                        subject = quiz.get("subject", "Unknown")
                        if subject not in subject_performance:
                            subject_performance[subject] = []
                        subject_performance[subject].append(attempt.get("percentage", 0))
                
                # Calculate average for each subject
                for subject in subject_performance:
                    if subject_performance[subject]:
                        subject_performance[subject] = sum(subject_performance[subject]) / len(subject_performance[subject])
            else:
                avg_score = 0
                avg_percentage = 0
                highest_score = 0
                lowest_score = 0
                subject_performance = {}
            
            # Progress over time
            progress_trend = []
            for attempt in completed_attempts:
                progress_trend.append({
                    "date": attempt["started_at"].strftime("%Y-%m-%d"),
                    "percentage": attempt.get("percentage", 0),
                    "subject": quiz_collection.find_one({"quiz_id": attempt["quiz_id"]}).get("subject", "Unknown")
                })
            
            progress_trend.sort(key=lambda x: x["date"])
            
            return {
                "success": True,
                "analytics": {
                    "period": period,
                    "total_attempts": total_attempts,
                    "completed_attempts": total_completed,
                    "completion_rate": (total_completed / total_attempts * 100) if total_attempts > 0 else 0,
                    "average_score": avg_score,
                    "average_percentage": avg_percentage,
                    "highest_score": highest_score,
                    "lowest_score": lowest_score,
                    "subject_performance": subject_performance,
                    "progress_trend": progress_trend
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate student analytics"
            }
    
    @staticmethod
    def export_analytics_to_csv(analytics_data, filename="analytics_report"):
        """Export analytics data to CSV format"""
        try:
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write summary section
            writer.writerow(["Analytics Report"])
            writer.writerow(["Period", analytics_data.get("period", "N/A")])
            writer.writerow(["Generated At", analytics_data.get("generated_at", "N/A")])
            writer.writerow([])
            
            # User analytics
            user_analytics = analytics_data.get("user_analytics", {})
            writer.writerow(["User Analytics"])
            writer.writerow(["Total New Users", user_analytics.get("total_new_users", 0)])
            writer.writerow(["Active Users", user_analytics.get("active_users_count", 0)])
            writer.writerow(["Activity Rate", f"{user_analytics.get('user_activity_rate', 0):.2f}%"])
            writer.writerow([])
            
            # Quiz analytics
            quiz_analytics = analytics_data.get("quiz_analytics", {})
            writer.writerow(["Quiz Analytics"])
            writer.writerow(["Total Quizzes Created", quiz_analytics.get("total_quizzes_created", 0)])
            writer.writerow(["Total Attempts", quiz_analytics.get("total_attempts", 0)])
            writer.writerow(["Completed Attempts", quiz_analytics.get("completed_attempts", 0)])
            writer.writerow(["Completion Rate", f"{quiz_analytics.get('completion_rate', 0):.2f}%"])
            writer.writerow([])
            
            # Performance analytics
            performance_analytics = analytics_data.get("performance_analytics", {})
            writer.writerow(["Performance Analytics"])
            writer.writerow(["Average Score", f"{performance_analytics.get('average_score', 0):.2f}"])
            writer.writerow(["Average Percentage", f"{performance_analytics.get('average_percentage', 0):.2f}%"])
            writer.writerow(["Highest Score", performance_analytics.get("highest_score", 0)])
            writer.writerow(["Lowest Score", performance_analytics.get("lowest_score", 0)])
            writer.writerow(["Pass Rate", f"{performance_analytics.get('pass_rate', 0):.2f}%"])
            writer.writerow([])
            
            csv_content = output.getvalue()
            output.close()
            
            return {
                "success": True,
                "csv_content": csv_content,
                "filename": f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to export analytics to CSV"
            }
