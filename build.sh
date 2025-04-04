#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Set environment variables for memory optimization
export WEB_CONCURRENCY=2
export PYTHON_GC_AGGRESSIVE=1
export PYTHONUNBUFFERED=1
export PYTHONOPTIMIZE=1 
