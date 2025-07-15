
# config.py - Configuration File
import os
from datetime import timedelta

class Config:
    """Application configuration"""
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://username:password@localhost:5432/dashboard')
    
    # Widget Configuration
    WIDGET_FOLDER = os.path.join(os.path.dirname(__file__), 'widgets')
    WIDGET_EXECUTION_INTERVAL = int(os.environ.get('WIDGET_EXECUTION_INTERVAL', 86400))  # 24 hours
    WIDGET_CHECK_INTERVAL = int(os.environ.get('WIDGET_CHECK_INTERVAL', 60))  # 1 minute
    WIDGET_TIMEOUT = int(os.environ.get('WIDGET_TIMEOUT', 300))  # 5 minutes
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
