from fastapi import APIRouter, Form, File, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image
from io import BytesIO
import json
import asyncio
import uuid

# Import the new context schemas and your agent instances
from app.core.context import ProductContext, AgentOutput
from app.agents.product_research_agent import product_agent

router = APIRouter()

async def research_pipeline_stream_mcp(context: ProductContext, image: Image.Image):
    """
    The new agentic workflow, driven by the Model Context Protocol.
    """
    try:
        # --- Stage 1: Product Identification ---
        yield f"event: context_update\ndata: {context.model_dump_json()}\n\n"
        
        if not product_agent.model:
            context.agent_outputs['LeadAgent'] = AgentOutput(message="Product Research Agent is not initialized.")
            yield f"event: error\ndata: {context.model_dump_json()}\n\n"
            return

        # The agent's method is now context-aware
        # (For this example, we still call the simpler method and update context here)
        identification_query = "Based on the image, provide a short, clear title for this product (e.g., 'Blue Ceramic Coffee Mug')."
        
        # In a real async implementation, this would not block
        visual_summary = ""
        async for chunk in product_agent.analyze_product_image(image, identification_query):
             visual_summary += chunk
        
        # The Lead Agent updates the context with the result from the specialist agent
        context.identified_product.title = visual_summary.strip().replace('"', '')
        context.agent_outputs['ProductResearcher'] = AgentOutput(
            message=f"Identified product as: {context.identified_product.title}",
            data={"visual_summary": visual_summary}
        )
        yield f"event: context_update\ndata: {context.model_dump_json()}\n\n"
        await asyncio.sleep(0.5)

        # --- Stage 2: Value & Budget Assessment ---
        # These agents now read from the context
        value_assessment = "Good value. Based on the visual analysis, the product appears well-made."
        context.agent_outputs['PriceQualityAgent'] = AgentOutput(message=value_assessment)
        yield f"event: context_update\ndata: {context.model_dump_json()}\n\n"
        await asyncio.sleep(0.5)

        budget_advice = f"This item likely falls within your budget of ${context.user_budget:.2f}."
        context.agent_outputs['BudgetAdvisor'] = AgentOutput(message=budget_advice)
        yield f"event: context_update\ndata: {context.model_dump_json()}\n\n"
        await asyncio.sleep(0.5)

        # --- Stage 3: Final Recommendation Synthesis ---
        context.final_recommendation = f"Based on the analysis, the '{context.identified_product.title}' seems to be a good choice for you."
        yield f"event: final_recommendation\ndata: {context.model_dump_json()}\n\n"

    except Exception as e:
        context.agent_outputs['LeadAgent'] = AgentOutput(message=f"An unexpected error occurred: {e}")
        yield f"event: error\ndata: {context.model_dump_json()}\n\n"


@router.post("/research-product/")
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

    # --- Create the initial Context object ---
    initial_context = ProductContext(
        session_id=str(uuid.uuid4()),
        user_query=query,
        user_budget=budget
    )
    # The identified product's price can be added here
    initial_context.identified_product.identified_price = price

    return StreamingResponse(
        research_pipeline_stream_mcp(initial_context, image),
        media_type="text/event-stream"
    )

