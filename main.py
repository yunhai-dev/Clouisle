#!/usr/bin/env python
"""
Clouisle Backend Startup Script
Run this file from the project root to start the backend server.
"""
import os
import sys
import subprocess

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

if __name__ == "__main__":
    # Use uvicorn to run the app
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[backend_dir],
    )
