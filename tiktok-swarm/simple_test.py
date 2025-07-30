"""Minimal FastAPI test"""
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!", "status": "working"}

if __name__ == "__main__":
    print("Starting minimal FastAPI test server...")
    print("Try: http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)