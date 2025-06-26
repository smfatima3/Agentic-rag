from fastapi import APIRouter, Form, File, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image
import asyncio
import json
from io import BytesIO  # <-- IMPORTANT: This import is needed to handle the image file

# Import your initialized agent instances from their respective files
from app.agents.product_research_agent import product_agent
# You would import your other agents here as well
# from app.agents.review_analyzer_agent import review_agent

# Create your FastAPI router
router = APIRouter()

async def research_pipeline_stream(query: str, budget: float, image: Image.Image):
    """
    The main agentic workflow, designed to be streamed to the frontend.
    It orchestrates calls to various specialized agents.
    """
    try:
        # --- Stage 1: Lead Agent validates inputs and starts the process ---
        yield "event: message\n"
        yield f"data: {json.dumps({'agent': 'Lead Agent', 'message': 'Request received. Starting analysis...'})}\n\n"
        await asyncio.sleep(0.5)

        # --- Stage 2: Product Research Agent identifies the product from the image ---
        if not product_agent.model:
            yield "event: error\n"
            yield f"data: {json.dumps({'agent': 'Lead Agent', 'message': 'Product Research Agent is not initialized. Cannot proceed.'})}\n\n"
            return
            
        yield "event: message\n"
        yield f"data: {json.dumps({'agent': 'Lead Agent', 'message': 'Asking Product Researcher to identify the item.'})}\n\n"
        await asyncio.sleep(0.5)

        identification_query = "Based on the image, provide a short, clear title for this product (e.g., 'Blue Ceramic Coffee Mug', 'Nike Air Max Running Shoe')."
        
        visual_summary = ""
        async for chunk in product_agent.analyze_product_image(image, identification_query):
            visual_summary += chunk
        
        yield "event: message\n"
        yield f"data: {json.dumps({'agent': 'Product Researcher', 'output': {'visual_summary': visual_summary}})}\n\n"
        await asyncio.sleep(0.5)

        # --- Stage 3: Other agents perform their tasks (currently mocked) ---
        # A real Review Analyzer would now search for reviews for the identified product.
        yield "event: message\n"
        yield f"data: {json.dumps({'agent': 'Review Analyzer', 'message': 'Found several similar products. The top match is a mock result.'})}\n\n"
        await asyncio.sleep(0.5)

        value_assessment = "Good value. The product appears to be well-made for its likely price point."
        yield "event: message\n"
        yield f"data: {json.dumps({'agent': 'Price-Quality Agent', 'output': {'value_assessment': value_assessment}})}\n\n"
        await asyncio.sleep(0.5)
        
        budget_advice = f"This item likely falls within your budget of ${budget:.2f}."
        yield "event: message\n"
        yield f"data: {json.dumps({'agent': 'Budget Advisor', 'output': {'budget_advice': budget_advice}})}\n\n"
        await asyncio.sleep(0.5)

        # --- Stage 4: Lead Agent compiles the final recommendation ---
        final_recommendation = {
            "title": visual_summary.strip().replace('"', ''),
            "visual_summary": "Analysis complete. See details above.",
            "value_assessment": value_assessment,
            "budget_advice": budget_advice,
        }

        yield "event: final_recommendation\n"
        yield f"data: {json.dumps(final_recommendation)}\n\n"

    except Exception as e:
        print(f"Error during stream: {e}")
        yield "event: error\n"
        yield f"data: {json.dumps({'agent': 'Lead Agent', 'message': f'An unexpected error occurred: {e}'})}\n\n"


@router.post("/research-product/")
async def run_product_research(
    query: str = Form(...),
    price: float = Form(...), 
    budget: float = Form(...),
    image_file: UploadFile = File(...)
):
    """
    The main API endpoint that receives the user's request and
    returns a streaming response of the agent's findings.
    """
    try:
        image_bytes = await image_file.read()
        image = Image.open(BytesIO(image_bytes)).convert("RGB")

        return StreamingResponse(
            research_pipeline_stream(query, budget, image),
            media_type="text/event-stream"
        )
    except Exception as e:
        print(f"Error in endpoint: {e}")
        error_message = json.dumps({'error': f'Failed to process request: {e}'})
        return StreamingResponse(
            iter([f"event: error\ndata: {error_message}\n\n"]),
            media_type="text/event-stream",
            status_code=500
        )
