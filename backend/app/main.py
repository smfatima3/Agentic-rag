# In backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # <--- IMPORT THIS
from app.api import endpoints
import os # <--- IMPORT THIS

app = FastAPI(
    title="Multi-Agent Shopping Assistant API",
    description="An API for a team of AI agents that help you find the perfect product.",
    version="1.0.0"
)

# You can keep your CORS settings
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This includes your /api/get-recommendation endpoint
app.include_router(endpoints.router, prefix="/api")

# --- THIS IS THE CRUCIAL NEW PART ---
# This line serves the built React app from the 'frontend/build' directory.
# It MUST come *after* your API router.
app.mount("/", StaticFiles(directory="/kaggle/working/Agentic-rag/frontend/build", html=True), name="static")
