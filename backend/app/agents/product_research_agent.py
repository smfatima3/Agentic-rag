# FILE: backend/app/agents/product_research_agent.py
# ACTION: Replace your existing file with this corrected code.

# First, ensure necessary libraries are installed for 4-bit quantization
try:
    import bitsandbytes
    import accelerate
except ImportError:
    raise ImportError("Please install 'bitsandbytes' and 'accelerate' for 4-bit quantization. Run: pip install bitsandbytes accelerate")

from transformers import AutoProcessor, LlavaForConditionalGeneration
from PIL import Image
import torch
import os

class ProductResearchAgent:
    def __init__(self):
        """
        Initializes the Product Research Agent by loading the LLaVA 1.5 model.
        This uses 4-bit quantization to reduce memory usage.
        Requires a GPU and a Hugging Face token set via Kaggle Secrets.
        """
        print("Initializing Product Research Agent with LLaVA...")
        
        # --- FIX: Rely on Kaggle Secrets for the token ---
        self.hf_token = os.environ.get('HF_TOKEN')
        if not self.hf_token:
            print("FATAL: Hugging Face token (HF_TOKEN) not found in Kaggle Secrets.")
            self.model = None
            self.processor = None
            return

        # --- FIX: Replaced text-only model with a powerful Vision-Language Model (VLM) ---
        self.model_id = "llava-hf/llava-1.5-7b-hf"
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        if self.device == "cpu":
            print("WARNING: Running LLaVA on CPU will be extremely slow.")

        try:
            # --- FIX: Use the correct model class and explicitly pass the token ---
            self.model = LlavaForConditionalGeneration.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16, # Use float16 for better compatibility on Kaggle GPUs
                low_cpu_mem_usage=True,
                load_in_4bit=True,
                token=self.hf_token # Explicitly pass the token here
            )
            self.processor = AutoProcessor.from_pretrained(self.model_id, token=self.hf_token)
            print("Product Research Agent initialized successfully.")

        except Exception as e:
            print(f"FATAL: Failed to load LLaVA model: {e}")
            print("Please check your internet connection, Hugging Face token, and that you have accepted the model's license on its Hugging Face page (if any).")
            self.model = None
            self.processor = None

    def analyze_image(self, image: Image.Image, prompt: str):
        """
        Analyzes an image using the LLaVA model.
        """
        if not self.model or not self.processor:
            return {
                "prompt": prompt,
                "analysis": "Sorry, the Product Research Agent is not initialized. Please check the server logs for fatal errors."
            }
            
        print(f"Agent received prompt: '{prompt}' for image analysis.")

        # --- FIX: Format the prompt for LLaVA ---
        prompt_template = f"USER: <image>\n{prompt}\nASSISTANT:"
        
        inputs = self.processor(text=prompt_template, images=image, return_tensors="pt").to(self.device)

        try:
            generated_ids = self.model.generate(**inputs, max_new_tokens=500)
            generated_texts = self.processor.batch_decode(generated_ids, skip_special_tokens=True)
            
            assistant_token = "ASSISTANT:"
            raw_text = generated_texts[0]
            assistant_start_index = raw_text.rfind(assistant_token)
            if assistant_start_index != -1:
                analysis_text = raw_text[assistant_start_index + len(assistant_token):].strip()
            else:
                analysis_text = "Could not parse the model's response."

        except Exception as e:
            print(f"An error occurred during model generation: {e}")
            analysis_text = f"Sorry, I encountered an error trying to analyze the image. Error: {e}"

        return {
            "prompt": prompt,
            "analysis": analysis_text
        }

# Singleton instance of the agent
product_agent = ProductResearchAgent()
