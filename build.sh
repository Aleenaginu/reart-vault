#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip

# Install face recognition dependencies from pre-built wheels
pip install --no-cache-dir cmake
pip install --no-cache-dir dlib-binary
pip install --no-cache-dir face-recognition

# Install other dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input 
