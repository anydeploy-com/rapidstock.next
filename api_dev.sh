#!/bin/bash
# Start the FastAPI dev server
cd api || { echo "api directory doesn't exist, exiting"; exit; }
uvicorn main:app --reload --host 0.0.0.0 --port 8000

