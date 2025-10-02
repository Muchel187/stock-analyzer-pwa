#!/usr/bin/env python3
"""Main application entry point"""

import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file (override existing)
load_dotenv(override=True)

# Verify critical API keys
if os.getenv('GOOGLE_API_KEY'):
    print(f"✅ GOOGLE_API_KEY loaded: {os.getenv('GOOGLE_API_KEY')[:20]}...")
else:
    print("⚠️  WARNING: GOOGLE_API_KEY not found!")

# Get configuration from environment
config_name = os.getenv('FLASK_ENV', 'development')

# Create application
app = create_app(config_name)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config['DEBUG']
    )