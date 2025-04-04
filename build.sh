#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install wheel
pip install cmake
pip install --no-cache-dir dlib==19.24.0
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input 
