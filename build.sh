#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies required for dlib and opencv
apt-get update
apt-get install -y cmake libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev python3-dev

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt 
