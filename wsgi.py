"""WSGI entry point for Vercel deployment"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

# Create application instance
app = create_app(os.getenv('FLASK_ENV', 'production'))

# Vercel expects the app to be named 'app' or 'application'
application = app

# For Vercel serverless function
def handler(request, response):
    """Vercel serverless function handler"""
    return app(request, response)

if __name__ == "__main__":
    # For local testing
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

