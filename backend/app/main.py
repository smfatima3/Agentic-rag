# In backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # Important for serving the frontend
from app.api import endpoints
import os

app = FastAPI(
    title="Multi-Agent Shopping Assistant API",
    description="An API for a team of AI agents that help you find the perfect product.",
    version="1.0.0"
)

# Your CORS settings are fine. This allows your frontend to talk to your backend.
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- THIS IS THE CHANGE ---
# The prefix="/api" has been removed.
# This makes your API endpoint directly accessible at /research-product/
# which matches the change we made to your frontend app.js
app.include_router(endpoints.router)

# This line serves the built React app. It should come AFTER your API routes.
# The path should point to the 'build' directory of your frontend.
# Make sure the path is correct for your server environment.
# Note: For Kaggle, this path might be different. 
# For a local setup, this assumes the backend is run from the project's root directory.
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "build")
if not os.path.exists(frontend_dir):
    print(f"WARNING: Frontend directory not found at {frontend_dir}. Static file serving will fail.")
else:
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")
