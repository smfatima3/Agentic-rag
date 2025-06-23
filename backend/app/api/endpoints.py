from fastapi import APIRouter, Form, File, UploadFile
from app.agents.review_analyzer_agent import review_agent
from app.agents.product_research_agent import product_agent
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from app.agents.lead_agent import lead_agent
from PIL import Image
import io

from PIL import Image
import io

router = APIRouter()

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

@router.post("/get-recommendation")
async def get_recommendation_stream(
    query: str = Form(...),
    price: float = Form(...),
    user_budget: float = Form(...),
    image: UploadFile = File(...)
):
    """
    The main endpoint that streams the analysis from all agents.
    """
    image_data = await image.read()
    pil_image = Image.open(io.BytesIO(image_data))
    
    # Return a streaming response that calls the lead agent's generator
    return StreamingResponse(
        lead_agent.run_analysis_stream(query, pil_image, price, user_budget),
        media_type="text/event-stream"
    )