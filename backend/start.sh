#!/bin/bash

# Start Jovey Backend
# Activates conda environment and starts FastAPI server

echo "🚀 Starting Jovey Backend..."

# Activate conda environment
source /home/gresh/miniconda3/bin/activate jovey

# Start uvicorn server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
