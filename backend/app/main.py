from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # Import this
from app.api import endpoints
import uvicorn


# Serve static React build
app.mount("/", StaticFiles(directory="frontend/build", html=True), name="frontend")

# CORS Middleware
origins = ["*"] # Allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(endpoints.router, prefix="/api")

# --- THIS IS THE NEW PART ---
# This will serve the static files from the React build folder
# It must come *after* the API router
app.mount("/", StaticFiles(directory="frontend/build", html=True), name="static")
