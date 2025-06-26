import torch
from transformers import (
    AutoTokenizer,
    AutoProcessor,
    Qwen2_5_VLForConditionalGeneration, # The CORRECT class for this model
    BitsAndBytesConfig
)
from PIL import Image
import requests
from io import BytesIO
import warnings

# Suppress the deprecation warning for a cleaner output
warnings.filterwarnings("ignore", category=FutureWarning, module="transformers.models.qwen2_5_vl.modeling_qwen2_5_vl")

class ProductResearchAgent:
    """
    An AI Agent that uses a Vision-Language Model to conduct product research
    by analyzing product images and textual descriptions.
    """
    def __init__(self, model_id="Qwen/Qwen2.5-VL-3B-Instruct"):
        """
        Initializes the agent and loads the necessary model components.
        """
        print(f"--- Initializing Product Research Agent with model: {model_id} ---")
        self.model_id = model_id
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        # Use BitsAndBytes for 4-bit quantization to save memory
        self.quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )

        self.model = self._load_model()
        self.processor = self._load_processor()
        print("\n✅ Agent initialized successfully.")

    def _load_model(self):
        """
        Loads the Qwen-VL model using its specific class to avoid errors.
        """
        print("Loading Qwen-VL model...")
        try:
            # THIS IS THE FIX: We use the specific class instead of AutoModelForCausalLM
            model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                self.model_id,
                quantization_config=self.quantization_config,
                device_map="auto",
                trust_remote_code=True,
            )
            return model
        except Exception as e:
            print(f"FATAL ERROR: Failed to load model '{self.model_id}'.")
            print(f"Error: {e}")
            raise

    def _load_processor(self):
        """
        Loads the processor, which includes the tokenizer and image processor.
        """
        print("Loading processor...")
        try:
            processor = AutoProcessor.from_pretrained(self.model_id, trust_remote_code=True)
            return processor
        except Exception as e:
            print(f"FATAL ERROR: Failed to load processor for '{self.model_id}'.")
            print(f"Error: {e}")
            raise

    def _load_image_from_url(self, image_url):
        """Helper function to load an image from a URL."""
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content)).convert("RGB")
            return image
        except requests.exceptions.RequestException as e:
            print(f"Error loading image from URL: {e}")
            return None

    def analyze_product(self, image_url, user_query):
        """
        Analyzes a product based on its image and a user's query.

        Args:
            image_url (str): The URL of the product image.
            user_query (str): The specific research question about the product.

        Returns:
            str: The model's analysis of the product.
        """
        print(f"\n--- Analyzing Product ---")
        print(f"Query: {user_query}")
        print(f"Image URL: {image_url}")

        image = self._load_image_from_url(image_url)
        if image is None:
            return "Could not load the product image."

        # Format the prompt for the Vision-Language Model
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": user_query}
                ]
            }
        ]
        
        # Use the processor to prepare all inputs
        text_prompt = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.processor(text_prompt, images=[image], return_tensors="pt").to(self.device)

        print("Generating analysis...")
        # Generate the response
        generated_ids = self.model.generate(**inputs, max_new_tokens=1024, do_sample=False)
        
        # Decode the output, skipping the prompt part
        input_token_len = inputs["input_ids"].shape[1]
        response_ids = generated_ids[:, input_token_len:]
        
        analysis = self.processor.batch_decode(response_ids, skip_special_tokens=True)[0]

        return analysis

# =================================================================
# Example Usage
# =================================================================
if __name__ == "__main__":
    # Initialize the agent
    # This will download and load the model, which may take some time and memory.
    try:
        product_agent = ProductResearchAgent()

        # --- Example 1: Research a specific product ---
        # Let's use an image of a running shoe
        shoe_image_url = "https://images.pexels.com/photos/1032110/pexels-photo-1032110.jpeg"
        
        query1 = (
            "As a product research agent, analyze this shoe. "
            "Describe its key features, material, and target audience. "
            "What are its potential strengths and weaknesses in the market?"
        )
        
        analysis_result = product_agent.analyze_product(shoe_image_url, query1)
        
        print("\n--- 📝 Product Analysis Report ---")
        print(analysis_result)
        
        # --- Example 2: Comparative question ---
        query2 = (
            "Based on the visual design, which competing brands does this shoe most resemble? "
            "Mention specific design cues like the sole pattern, upper mesh, and overall silhouette."
        )

        comparative_analysis = product_agent.analyze_product(shoe_image_url, query2)
        print("\n--- 📝 Comparative Analysis Report ---")
        print(comparative_analysis)

    except Exception as e:
        print(f"\nAn error occurred during agent execution: {e}")
