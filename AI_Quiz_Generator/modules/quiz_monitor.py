"""
Quiz Monitoring Module
Handles real-time monitoring and malactivity detection during quizzes
"""

import datetime
from config import quiz_attempts_collection
from modules.database_models import QuizAttemptModels

class QuizMonitor:
    """Monitors quiz attempts and detects malactivity"""
    
    @staticmethod
    def log_malactivity_event(attempt_id, event_type, additional_data=None):
        """Log a malactivity event for a quiz attempt"""
        try:
            # Get current attempt
            attempt = quiz_attempts_collection.find_one({"attempt_id": attempt_id})
            if not attempt:
                return {"success": False, "message": "Attempt not found"}
            
            # Create malactivity event
            event = QuizAttemptModels.create_malactivity_event()
            event.update({
                "event_type": event_type,
                "additional_data": additional_data or {}
            })
            
            # Update attempt
            current_warnings = attempt.get("warnings", 0)
            new_warnings = current_warnings + 1
            
            # Get max warnings from quiz settings
            max_warnings = 3  # Default, should be fetched from quiz settings
            
            action_taken = "warning"
            if new_warnings >= max_warnings:
                action_taken = "auto_submit"
                # Auto-submit the quiz
                quiz_attempts_collection.update_one(
                    {"attempt_id": attempt_id},
                    {
                        "$push": {"malactivity_detected": event},
                        "$set": {
                            "warnings": new_warnings,
                            "status": "auto_submitted",
                            "submitted_at": datetime.datetime.now()
                        }
                    }
                )
                return {
                    "success": True,
                    "warnings": new_warnings,
                    "action_taken": action_taken,
                    "message": f"Quiz auto-submitted due to {max_warnings} malactivity warnings"
                }
            else:
                quiz_attempts_collection.update_one(
                    {"attempt_id": attempt_id},
                    {
                        "$push": {"malactivity_detected": event},
                        "$set": {"warnings": new_warnings}
                    }
                )
                return {
                    "success": True,
                    "warnings": new_warnings,
                    "action_taken": action_taken,
                    "message": f"Warning {new_warnings}/{max_warnings}: {event_type} detected"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to log malactivity event"
            }
    
    @staticmethod
    def check_attempt_status(attempt_id):
        """Check current status and warnings for an attempt"""
        try:
            attempt = quiz_attempts_collection.find_one({"attempt_id": attempt_id})
            if not attempt:
                return {"success": False, "message": "Attempt not found"}
            
            return {
                "success": True,
                "status": attempt.get("status"),
                "warnings": attempt.get("warnings", 0),
                "malactivity_events": attempt.get("malactivity_detected", []),
                "started_at": attempt.get("started_at"),
                "submitted_at": attempt.get("submitted_at")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to check attempt status"
            }
    
    @staticmethod
    def get_active_attempts(quiz_code):
        """Get all currently active attempts for a quiz"""
        try:
            attempts = list(quiz_attempts_collection.find({
                "quiz_code": quiz_code.upper(),
                "status": "in_progress"
            }))
            
            # Format for monitoring dashboard
            active_attempts = []
            for attempt in attempts:
                active_attempts.append({
                    "attempt_id": attempt["attempt_id"],
                    "student_name": attempt["student_name"],
                    "register_number": attempt["register_number"],
                    "started_at": attempt["started_at"],
                    "warnings": attempt.get("warnings", 0),
                    "last_activity": attempt.get("last_activity", attempt["started_at"]),
                    "malactivity_count": len(attempt.get("malactivity_detected", []))
                })
            
            return {
                "success": True,
                "active_attempts": active_attempts,
                "total_active": len(active_attempts)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to fetch active attempts"
            }
    
    @staticmethod
    def update_last_activity(attempt_id):
        """Update the last activity timestamp for an attempt"""
        try:
            result = quiz_attempts_collection.update_one(
                {"attempt_id": attempt_id, "status": "in_progress"},
                {"$set": {"last_activity": datetime.datetime.now()}}
            )
            
            return {
                "success": result.modified_count > 0,
                "message": "Activity updated" if result.modified_count > 0 else "Attempt not found or not active"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to update activity"
            }
    
    @staticmethod
    def force_submit_attempt(attempt_id, reason="Teacher intervention"):
        """Force submit a quiz attempt (for teachers)"""
        try:
            attempt = quiz_attempts_collection.find_one({"attempt_id": attempt_id})
            if not attempt:
                return {"success": False, "message": "Attempt not found"}
            
            if attempt["status"] != "in_progress":
                return {"success": False, "message": "Attempt is not in progress"}
            
            # Calculate score (simplified - should be based on actual answers)
            score = 0  # TODO: Calculate actual score from answers
            
            quiz_attempts_collection.update_one(
                {"attempt_id": attempt_id},
                {
                    "$set": {
                        "status": "submitted",
                        "submitted_at": datetime.datetime.now(),
                        "score": score,
                        "percentage": (score / attempt["total_marks"]) * 100 if attempt["total_marks"] > 0 else 0,
                        "time_taken_seconds": (datetime.datetime.now() - attempt["started_at"]).total_seconds(),
                        "force_submit_reason": reason
                    }
                }
            )
            
            return {
                "success": True,
                "message": f"Quiz force submitted: {reason}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to force submit attempt"
            }
    
    @staticmethod
    def get_monitoring_data(quiz_code):
        """Get comprehensive monitoring data for a quiz"""
        try:
            # Get active attempts
            active_result = QuizMonitor.get_active_attempts(quiz_code)
            
            # Get all attempts for statistics
            all_attempts = list(quiz_attempts_collection.find({
                "quiz_code": quiz_code.upper()
            }))
            
            # Calculate statistics
            total_attempts = len(all_attempts)
            completed_attempts = len([a for a in all_attempts if a["status"] in ["submitted", "auto_submitted"]])
            auto_submitted = len([a for a in all_attempts if a["status"] == "auto_submitted"])
            
            # Malactivity statistics
            total_warnings = sum(a.get("warnings", 0) for a in all_attempts)
            students_with_warnings = len([a for a in all_attempts if a.get("warnings", 0) > 0])
            
            return {
                "success": True,
                "monitoring_data": {
                    "quiz_code": quiz_code,
                    "total_attempts": total_attempts,
                    "completed_attempts": completed_attempts,
                    "active_attempts": active_result.get("active_attempts", []),
                    "auto_submitted": auto_submitted,
                    "total_warnings": total_warnings,
                    "students_with_warnings": students_with_warnings,
                    "completion_rate": (completed_attempts / total_attempts * 100) if total_attempts > 0 else 0
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get monitoring data"
            }

class ClientSideMonitor:
    """Client-side monitoring functions to be used in JavaScript"""
    
    @staticmethod
    def get_monitoring_script(attempt_id, max_warnings=3):
        """Generate JavaScript code for client-side monitoring"""
        script = f"""
        // Quiz Monitoring System
        let attemptId = '{attempt_id}';
        let warnings = 0;
        let maxWarnings = {max_warnings};
        let malactivityLog = [];
        
        // Track page visibility
        let hidden, visibilityChange;
        if (typeof document.hidden !== "undefined") {{
            hidden = "hidden";
            visibilityChange = "visibilitychange";
        }} else if (typeof document.msHidden !== "undefined") {{
            hidden = "msHidden";
            visibilityChange = "msvisibilitychange";
        }} else if (typeof document.webkitHidden !== "undefined") {{
            hidden = "webkitHidden";
            visibilityChange = "webkitvisibilitychange";
        }}
        
        // Handle visibility change
        function handleVisibilityChange() {{
            if (document[hidden]) {{
                logMalactivity('tab_switch', 'Tab switched or window hidden');
            }} else {{
                updateActivity();
            }}
        }}
        
        // Log malactivity event
        function logMalactivity(eventType, details) {{
            warnings++;
            const event = {{
                timestamp: new Date().toISOString(),
                type: eventType,
                details: details,
                warningNumber: warnings
            }};
            
            malactivityLog.push(event);
            
            // Send to server
            fetch('/log_malactivity', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify({{
                    attempt_id: attemptId,
                    event_type: eventType,
                    details: details
                }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.action_taken === 'auto_submit') {{
                    // Quiz was auto-submitted
                    alert('Quiz auto-submitted due to multiple warnings!');
                    window.location.href = '/result/' + attemptId;
                }} else {{
                    // Show warning
                    showWarning(data.message);
                }}
            }})
            .catch(error => console.error('Error logging malactivity:', error));
        }}
        
        // Show warning to user
        function showWarning(message) {{
            const warningDiv = document.createElement('div');
            warningDiv.className = 'alert alert-warning';
            warningDiv.innerHTML = `
                <i class="fas fa-exclamation-triangle"></i> ${message}
                <span class="warning-count">Warning ${{warnings}}/${{maxWarnings}}</span>
            `;
            warningDiv.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                min-width: 300px;
                animation: slideIn 0.3s ease-out;
            `;
            
            document.body.appendChild(warningDiv);
            
            // Auto remove after 5 seconds
            setTimeout(() => {{
                if (warningDiv.parentNode) {{
                    warningDiv.parentNode.removeChild(warningDiv);
                }}
            }}, 5000);
        }}
        
        // Update activity timestamp
        function updateActivity() {{
            fetch('/update_activity', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify({{
                    attempt_id: attemptId
                }})
            }})
            .catch(error => console.error('Error updating activity:', error));
        }}
        
        // Prevent right-click
        document.addEventListener('contextmenu', function(e) {{
            e.preventDefault();
            logMalactivity('right_click', 'Right-click attempted');
            return false;
        }});
        
        // Prevent copy/paste
        document.addEventListener('copy', function(e) {{
            e.preventDefault();
            logMalactivity('copy_paste', 'Copy attempted');
            return false;
        }});
        
        document.addEventListener('paste', function(e) {{
            e.preventDefault();
            logMalactivity('copy_paste', 'Paste attempted');
            return false;
        }});
        
        // Prevent text selection
        document.addEventListener('selectstart', function(e) {{
            e.preventDefault();
            return false;
        }});
        
        // Track keyboard shortcuts
        document.addEventListener('keydown', function(e) {{
            // Prevent Ctrl+C, Ctrl+V, Ctrl+X
            if (e.ctrlKey && (e.key === 'c' || e.key === 'v' || e.key === 'x')) {{
                e.preventDefault();
                logMalactivity('keyboard_shortcut', 'Copy/paste shortcut attempted');
                return false;
            }}
            
            // Prevent F12, Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+U
            if (e.key === 'F12' || 
                (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'J')) ||
                (e.ctrlKey && e.key === 'U')) {{
                e.preventDefault();
                logMalactivity('dev_tools', 'Developer tools attempted');
                return false;
            }}
        }});
        
        // Track window focus/blur
        window.addEventListener('blur', function() {{
            logMalactivity('window_focus_lost', 'Window lost focus');
        }});
        
        window.addEventListener('focus', function() {{
            updateActivity();
        }});
        
        // Setup visibility change listener
        if (typeof document.addEventListener === "undefined" || hidden === undefined) {{
            console.log("Page Visibility API not supported");
        }} else {{
            document.addEventListener(visibilityChange, handleVisibilityChange, false);
        }}
        
        // Update activity every 30 seconds
        setInterval(updateActivity, 30000);
        
        // Initial activity update
        updateActivity();
        
        console.log('Quiz monitoring initialized for attempt:', attemptId);
        """
        
        return script
