import os
from dotenv import load_dotenv

load_dotenv()

# Configuration class for the Flask application. It loads environment variables for sensitive information like SECRET_KEY 
# and DATABASE_URL, providing default values if they are not set. This class is used to centralize configuration settings and keep them separate from the application logic.
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False