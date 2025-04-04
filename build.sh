#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies
apt-get update && apt-get install -y cmake build-essential pkg-config
apt-get install -y libx11-dev libatlas-base-dev
apt-get install -y libgtk-3-dev libboost-python-dev
apt-get install -y python3-dev python3-pip
apt-get install -y libopencv-dev

# Install Python dependencies
pip install --upgrade pip

# Install dlib with specific compiler flags
DLIB_USE_CUDA=0 pip install dlib==19.22.1

# Install other dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input 
