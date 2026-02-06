"""
Vercel serverless function entry point for FastAPI application.
This file is required for Vercel to properly serve the FastAPI app.
"""
import sys
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from server import app

# Vercel will use this 'app' object
# No need for uvicorn.run() as Vercel handles that
