from fastapi import APIRouter, Form, File, UploadFile, Request
from fastapi.responses import StreamingResponse
from PIL import Image
import asyncio
import json

# Import your initialized agent instances
# FastAPI will load these on startup. Check your console for initialization logs.
from app.agents.product_research_agent import product_agent
# Mock other agents for demonstration purposes
from app.agents.review_analyzer_agent import review_agent
from app.agents.budget_advisor_agent import budget_advisor

# Create your FastAPI router
router = APIRouter()

async def research_pipeline_stream(query: str, budget: float, image: Image.Image):
    """
    The main agentic workflow, designed to be streamed.
    It orchestrates calls to various agents.
    """
    # --- Stage 1: Initial Validation & Product Identification ---
    # A real 'review_agent' would search online based on the query.
    # Here, we'll use the Product Research Agent to identify the item in the image first.
    
    yield "event: message\n"
    yield f"data: {json.dumps({'agent': 'Lead Agent', 'message': 'Starting analysis... Identifying product from image.'})}\n\n"
    await asyncio.sleep(0.5)

    if not product_agent.model:
        yield "event: error\n"
        yield f"data: {json.dumps({'agent': 'Lead Agent', 'message': 'Product Research Agent failed to initialize. Cannot proceed.'})}\n\n"
        return

    # Use the visual agent to get a description
    identification_query = "Based on the image, provide a short, clear title for this product (e.g., 'Blue Ceramic Coffee Mug', 'Nike Air Max Running Shoe')."
    
    # The analyze_product_image is an async generator, so we must iterate over it
    visual_summary = ""
    async for chunk in product_agent.analyze_product_image(image, identification_query):
        visual_summary += chunk
    
    yield "event: message\n"
    yield f"data: {json.dumps({'agent': 'Product Researcher', 'output': {'visual_summary': visual_summary}})}\n\n"
    await asyncio.sleep(0.5)

    # --- Stage 2: Value & Budget Assessment (Mock Agents) ---
    # In a real app, these agents would take the identified product and price
    
    value_assessment = "Good value. The product appears to be well-made for its likely price point, based on visual features."
    yield "event: message\n"
    yield f"data: {json.dumps({'agent': 'Price-Quality Agent', 'output': {'value_assessment': value_assessment}})}\n\n"
    await asyncio.sleep(0.5)
    
    budget_advice = f"This item likely falls within your budget of ${budget:.2f}."
    yield "event: message\n"
    yield f"data: {json.dumps({'agent': 'Budget Advisor', 'output': {'budget_advice': budget_advice}})}\n\n"
    await asyncio.sleep(0.5)

    # --- Stage 3: Final Recommendation ---
    final_recommendation = {
        "title": visual_summary.strip().replace('"', ''),
        "visual_summary": "Analysis complete. See details above.",
        "value_assessment": value_assessment,
        "budget_advice": budget_advice,
    }

    yield "event: final_recommendation\n"
    yield f"data: {json.dumps(final_recommendation)}\n\n"


@router.post("/research-product/")
async def run_product_research(
    query: str = Form(...),
    price: float = Form(...), # Assuming price comes from the form
    budget: float = Form(...),
    image_file: UploadFile = File(...)
):
    """
    The main API endpoint that receives the user's request and
    returns a streaming response of the agent's findings.
    """
    try:
        # Read the uploaded image file into a PIL Image
        image_bytes = await image_file.read()
        image = Image.open(BytesIO(image_bytes)).convert("RGB")

        # Return a streaming response that calls our agent pipeline
        return StreamingResponse(
            research_pipeline_stream(query, budget, image),
            media_type="text/event-stream"
        )
    except Exception as e:
        print(f"Error in endpoint: {e}")
        return StreamingResponse(
            iter([f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"]),
            media_type="text/event-stream",
            status_code=500
        )
