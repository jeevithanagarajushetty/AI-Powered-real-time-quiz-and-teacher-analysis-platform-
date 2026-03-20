from pymongo import MongoClient
import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["ai_quiz_system"]

# Collections
users_collection = db["users"]
quiz_collection = db["quiz"]
quiz_attempts_collection = db["quiz_attempts"]
quiz_codes_collection = db["quiz_codes"]
results_collection = db["results"]
analytics_collection = db["analytics"]
subjects_collection = db["subjects"]