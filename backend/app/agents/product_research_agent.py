import torch
from transformers import (
    AutoProcessor,
    Qwen2_5_VLForConditionalGeneration,
    BitsAndBytesConfig
)
from PIL import Image
import warnings
import traceback

# Suppress known warnings for a cleaner console
warnings.filterwarnings("ignore", category=FutureWarning)

class ProductResearchAgent:
    """
    An AI Agent that uses Qwen-VL to conduct deep analysis of product images.
    This version includes enhanced logging for better debugging in a web app.
    """
    def __init__(self, model_id="Qwen/Qwen2.5-VL-3B-Instruct"):
        self.model_id = model_id
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.processor = None
        
        # This will be called when the agent is initialized at app startup.
        self._load_model_and_processor()

    def _load_model_and_processor(self):
        """
        Loads the necessary model and processor components.
        This is a resource-intensive operation.
        """
        print(f"--- [ProductResearchAgent] Initializing with model: {self.model_id} ---")
        print(f"--- [ProductResearchAgent] Using device: {self.device} ---")

        if self.device == "cpu":
            print("WARNING: [ProductResearchAgent] Running on CPU. Performance will be very slow.")
        
        try:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
            )
            
            self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                self.model_id,
                quantization_config=quantization_config,
                device_map="auto",
                trust_remote_code=True,
            )
            self.processor = AutoProcessor.from_pretrained(self.model_id, trust_remote_code=True)
            print("✅ [ProductResearchAgent] Model and processor loaded successfully.")
        except Exception as e:
            print("❌ FATAL ERROR: [ProductResearchAgent] Failed to initialize.")
            print(f"Error: {e}")
            print("Full Traceback:")
            traceback.print_exc()
            self.model = None
            self.processor = None

    async def analyze_product_image(self, image: Image.Image, query: str):
        """
        Analyzes a product image and yields the analysis.
        """
        if not self.model or not self.processor:
            print("ERROR: [ProductResearchAgent] Analysis called but agent is not initialized.")
            yield "Product Research Agent is not initialized. Please check server logs for errors."
            return

        print(f"--- [ProductResearchAgent] Starting analysis for query: '{query[:30]}...' ---")
        messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": query}]}]
        text_prompt = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.processor(text_prompt, images=[image], return_tensors="pt").to(self.device)

        generated_ids = self.model.generate(**inputs, max_new_tokens=1024, do_sample=False)
        input_token_len = inputs["input_ids"].shape[1]
        response_ids = generated_ids[:, input_token_len:]
        
        analysis = self.processor.batch_decode(response_ids, skip_special_tokens=True)[0]
        print(f"--- [ProductResearchAgent] Analysis generation complete. ---")
        
        yield analysis

# --- Global Agent Instance ---
# The application will create one instance of this agent on startup.
product_agent = ProductResearchAgent()

