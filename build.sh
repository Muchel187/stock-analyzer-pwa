#!/bin/bash
# Render build script

echo "Starting build process..."

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations
echo "Running database migrations..."
flask db upgrade

echo "Build complete!"
