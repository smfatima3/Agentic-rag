# In backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import endpoints
import os

app = FastAPI(
    title="Multi-Agent Shopping Assistant API",
    description="An API for a team of AI agents that help you find the perfect product.",
    version="1.0.0"
)

# Your CORS settings
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(endpoints.router, prefix="/api")

# This serves your frontend app. This part is correct and should come last.
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "build")
if not os.path.exists(frontend_dir):
    print(f"WARNING: Frontend directory not found at {frontend_dir}. Static file serving will fail.")
else:
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")
