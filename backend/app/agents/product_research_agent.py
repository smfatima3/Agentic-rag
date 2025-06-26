import torch
from transformers import (
    AutoTokenizer,
    AutoProcessor,
    Qwen2_5_VLForConditionalGeneration,
    BitsAndBytesConfig
)
from PIL import Image
import requests
from io import BytesIO
import warnings
import traceback

# Suppress known warnings for a cleaner console
warnings.filterwarnings("ignore", category=FutureWarning)

class ProductResearchAgent:
    """
    An AI Agent that uses Qwen-VL to conduct deep analysis of product images.
    """
    def __init__(self, model_id="Qwen/Qwen2.5-VL-3B-Instruct"):
        self.model_id = model_id
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.processor = None
        
        # This will be called when the agent is initialized
        self._load_model_and_processor()

    def _load_model_and_processor(self):
        """
        Loads the necessary model and processor components.
        This is a resource-intensive operation.
        """
        print(f"--- Initializing Product Research Agent with model: {self.model_id} ---")
        print(f"Using device: {self.device}")

        if self.device == "cpu":
            print("WARNING: Running on CPU. Performance will be very slow.")
        
        try:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
            )
            
            # Use the specific class to avoid loading errors
            self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                self.model_id,
                quantization_config=quantization_config,
                device_map="auto",
                trust_remote_code=True,
            )
            self.processor = AutoProcessor.from_pretrained(self.model_id, trust_remote_code=True)
            print("✅ Product Research Agent model and processor loaded successfully.")
        except Exception as e:
            print("❌ FATAL ERROR: Failed to initialize ProductResearchAgent.")
            print(f"Error: {e}")
            print("Full Traceback:")
            traceback.print_exc()
            # The agent will remain uninitialized if this fails
            self.model = None
            self.processor = None

    async def analyze_product_image(self, image: Image.Image, query: str):
        """
        Analyzes a product image and yields the analysis in chunks for streaming.
        
        Args:
            image (PIL.Image.Image): The product image.
            query (str): The specific research question about the product.

        Yields:
            str: Chunks of the analysis text.
        """
        if not self.model or not self.processor:
            yield "Product Research Agent is not initialized. Check server logs for errors."
            return

        messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": query}]}]
        text_prompt = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.processor(text_prompt, images=[image], return_tensors="pt").to(self.device)

        # Using generate with a streamer for real-time output
        # This is a placeholder for a more complex streaming logic if needed.
        # For simplicity, we'll generate the full text and then yield it.
        # A more advanced implementation would use a custom streamer object.
        
        print("Product Researcher: Generating visual analysis...")
        generated_ids = self.model.generate(**inputs, max_new_tokens=1024, do_sample=False)
        input_token_len = inputs["input_ids"].shape[1]
        response_ids = generated_ids[:, input_token_len:]
        
        analysis = self.processor.batch_decode(response_ids, skip_special_tokens=True)[0]
        
        # Yield the final result as a single chunk
        yield analysis

# --- Global Agent Instance ---
# The application will create one instance of this agent on startup.
product_agent = ProductResearchAgent()
