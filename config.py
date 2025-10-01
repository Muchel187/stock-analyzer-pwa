import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///stockanalyzer.db')
    
    # Fix for Render.com DATABASE_URL format issues (remove "DATABASE_URL=" prefix if present)
    if DATABASE_URL and '=' in DATABASE_URL and DATABASE_URL.startswith('DATABASE_URL='):
        DATABASE_URL = DATABASE_URL.split('=', 1)[1]
    
    # Fix for Heroku postgres:// vs postgresql://
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Redis/Cache
    CACHE_TYPE = "redis" if os.environ.get('REDIS_URL') else "simple"
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('STOCKS_CACHE_TIMEOUT', 3600))

    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')

    # API Keys
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')

    # App Settings
    PORTFOLIO_UPDATE_INTERVAL = int(os.environ.get('PORTFOLIO_UPDATE_INTERVAL', 300))
    ALERT_CHECK_INTERVAL = int(os.environ.get('ALERT_CHECK_INTERVAL', 60))

    # Supported Markets
    SUPPORTED_MARKETS = ['USA', 'DAX']

    # Screener Defaults
    SCREENER_MAX_RESULTS = 100

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # Additional production settings
    SESSION_COOKIE_SECURE = True  # Requires HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # CORS for production
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    # Ensure proper database connection
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}