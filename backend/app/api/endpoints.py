from fastapi import APIRouter, Form, File, UploadFile
from app.agents.review_analyzer_agent import review_agent
from app.agents.product_research_agent import product_agent
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from app.agents.lead_agent import LeadAgent
import asyncio
import json
from PIL import Image
import io

router = APIRouter()

@router.get("/api/get-recommendation")
async def get_recommendation(
    query: str,
    price: float,
    user_budget: float,
    # The image will be handled by the lead agent, assuming it's passed through other means
    # for a GET request. For a real-world scenario with image upload, a POST
    # request would be more suitable, but we'll stick to the plan for SSE.
):
    lead_agent = LeadAgent()

    async def event_stream():
        # This simulates the image being available to the agent
        # In a real app, you might save the image from a POST and retrieve it here
        # based on a session or task ID.
        image_bytes = None # Placeholder for where you'd get the image data

        async for update in lead_agent.run_agents(query, price, user_budget, image_bytes):
            yield f"data: {json.dumps(update)}\n\n"
            await asyncio.sleep(0.1) # Small delay to ensure messages are sent separately

    return StreamingResponse(event_stream(), media_type="text/event-stream")

# You might have a separate endpoint to upload the image first
@router.post("/api/upload-image")
async def upload_image(image: UploadFile = File(...)):
    # Logic to save the image and return an identifier
    return {"filename": image.filename}

# You would then pass the image identifier to the get-recommendation endpoint

@router.post("/analyze-reviews")
async def analyze_reviews(query: str = Form(...)):
    """
    Endpoint to get an analysis of product reviews based on a user query.
    """
    analysis = review_agent.analyze(query)
    return analysis


@router.post("/analyze-product-image")
async def analyze_product_image(prompt: str = Form(...), image: UploadFile = File(...)):
    """
    Endpoint to analyze a product image with a prompt using the Product Research Agent.
    """
    image_bytes = await image.read()
    pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    analysis = product_agent.analyze_image(pil_image, prompt)
    return analysis