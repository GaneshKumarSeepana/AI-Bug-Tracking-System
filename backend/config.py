import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
    # Using Local MongoDB Community Server for reliability and speed
    # For cloud deployment, set MONGO_URI in .env file
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/bug_tracker_db")
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

