# FastAPI RapidStock API

This folder contains the FastAPI backend API for RapidStock.

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the API

Development server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or using FastAPI CLI:
```bash
fastapi dev main.py
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc