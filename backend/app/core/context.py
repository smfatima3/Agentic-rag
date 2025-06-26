from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

# Pydantic models define the structure of your data.

class Product(BaseModel):
    """
    A structured representation of the identified product.
    This is a sub-document within our main context.
    """
    title: Optional[str] = None
    identified_price: Optional[float] = None
    image_url: Optional[str] = None # If found online
    visual_summary: Optional[str] = None
    value_assessment: Optional[str] = None
    
class AgentOutput(BaseModel):
    """
    A generic model to hold the output from any agent.
    """
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class ProductContext(BaseModel):
    """
    The main Context object - our "shared whiteboard".
    This object will be created for each request and passed between agents.
    """
    session_id: str
    user_query: str
    user_budget: float
    
    # The product that the agents are currently analyzing.
    # It starts empty and gets filled in by the agents.
    identified_product: Product = Field(default_factory=Product)
    
    # A dictionary to hold the final output from each agent.
    agent_outputs: Dict[str, AgentOutput] = Field(default_factory=dict)
    
    # The final recommendation synthesized from all agent outputs.
    final_recommendation: Optional[str] = None

