#!/usr/bin/env python3
"""
NarrativeForge Backend Startup Script
Simple script to start the backend server
"""

import os
import sys
import subprocess

def main():
    """Start the NarrativeForge backend server"""
    
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    
    print("🚀 Starting NarrativeForge Backend...")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Check if requirements are installed
    try:
        import fastapi
        import transformers
        print("✅ Dependencies found")
    except ImportError:
        print("❌ Dependencies not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Start the server
    print("🌐 Starting server on http://localhost:8000")
    print("📚 API documentation available at http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
