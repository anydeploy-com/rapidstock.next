#!/bin/bash
# Start the frontend Nuxt dev server
cd frontend
npm run dev
# Start the FastAPI dev server
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000

