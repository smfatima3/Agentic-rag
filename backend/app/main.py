from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import endpoints
import uvicorn

app = FastAPI(
    title="Multi-Agent Shopping Assistant API",
    description="An API for a team of AI agents that help you find the perfect product.",
    version="1.0.0"
)

# CORS Middleware
origins = ["*"] # Allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router from our endpoints file
app.include_router(endpoints.router, prefix="/api", tags=["Agents"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Multi-Agent Shopping Assistant API!"}

# Note: The visual QA endpoint has been removed for now and will be
# reintroduced in Phase 3 with the Product Research Agent.

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
