from fastapi import FastAPI

app = FastAPI(title="RapidStock API", description="FastAPI backend for RapidStock", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Welcome to RapidStock API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}