#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip

# Install face recognition dependencies using specific versions
pip install --no-cache-dir numpy==1.24.3
pip install --no-cache-dir "dlib @ https://github.com/jloh02/dlib/releases/download/v19.24/dlib-19.24.0-cp311-cp311-linux_x86_64.whl"
pip install --no-cache-dir face-recognition

# Install other dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input 
