#!/usr/bin/env python3
"""
Simple test to verify FastAPI works with our setup
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Test API")

@app.get("/")
async def read_root():
    return {"message": "Hello AndyGoogle!"}

@app.get("/test")
async def test_database():
    import sqlite3
    try:
        conn = sqlite3.connect('Data/Local/cached_library.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM books')
        count = cursor.fetchone()[0]
        conn.close()
        return {"books": count, "status": "success"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}

if __name__ == "__main__":
    print("🧪 Testing basic FastAPI functionality...")
    print("🌐 Server accessible from any device on your network")
    uvicorn.run(app, host="0.0.0.0", port=8003)