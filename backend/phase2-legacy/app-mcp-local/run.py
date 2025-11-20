#!/usr/bin/env python3
"""
Main entry point for AAP project
Usage: python run.py
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Import and run server
import uvicorn

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════╗
║        AAP Project Started           ║
╠══════════════════════════════════════╣
║  API: http://localhost:8000/api      ║
║  Dashboard: http://localhost:8000    ║
╚══════════════════════════════════════╝
    """)
    
    uvicorn.run("backend.server:app", host="0.0.0.0", port=8000, reload=True)

    