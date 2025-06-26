from fastapi import APIRouter, Form, File, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image
from io import BytesIO
import json
import asyncio
import uuid

# Import your context schema and agent instances
from app.core.context import ProductContext
from app.agents.product_research_agent import product_agent

router = APIRouter()

# The research pipeline stream function remains the same
async def research_pipeline_stream_mcp(context: ProductContext, image: Image.Image):
    """
    The agentic workflow, driven by the Model Context Protocol.
    """
    # (No changes needed inside this function)
    try:
        # --- Stage 1: Lead Agent validates inputs and starts the process ---
        yield f"event: context_update\ndata: {context.model_dump_json()}\n\n"
        
        if not product_agent.model:
            # ... (rest of the logic)
            return

        # ... (rest of your agent logic) ...
        
        # --- Final Recommendation Synthesis ---
        context.final_recommendation = f"Based on the analysis, the '{context.identified_product.title}' seems to be a good choice for you."
        yield f"event: final_recommendation\ndata: {context.model_dump_json()}\n\n"

    except Exception as e:
        # ... (error handling logic)
        pass


# =========================================================
# === THIS IS THE FIX ===
# Change the endpoint path back to what the frontend is calling.
# =========================================================
@router.post("/get-recommendation")
async def run_product_research(
    query: str = Form(...),
    price: float = Form(...), 
    budget: float = Form(...),
    image_file: UploadFile = File(...)
):
    """
    This endpoint initializes the Context and starts the agent workflow.
    """
    image_bytes = await image_file.read()
    image = Image.open(BytesIO(image_bytes)).convert("RGB")

    initial_context = ProductContext(
        session_id=str(uuid.uuid4()),
        user_query=query,
        user_budget=budget
    )
    initial_context.identified_product.identified_price = price

    return StreamingResponse(
        research_pipeline_stream_mcp(initial_context, image),
        media_type="text/event-stream"
    )

