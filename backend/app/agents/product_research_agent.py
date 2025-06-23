# FILE: backend/app/agents/product_research_agent.py
# ACTION: Replace this file's content entirely.

from transformers import AutoModelForCausalLM, AutoProcessor
from PIL import Image
import torch
import os

class ProductResearchAgent:
    def __init__(self):
        """
        Initializes the agent with the Qwen/Qwen2.5-VL-3B-Instruct model.
        """
        print("Initializing Product Research Agent with Qwen-VL...")
        
        if 'HF_TOKEN' not in os.environ:
            print("WARNING: Hugging Face token (HF_TOKEN) not found.")
            self.model = self.processor = None
            return

        self.model_id = "Qwen/Qwen2.5-VL-3B-Instruct"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                torch_dtype=torch.bfloat16,
                device_map=self.device,
                trust_remote_code=True
            )
            self.processor = AutoProcessor.from_pretrained(self.model_id, trust_remote_code=True)
            print("Product Research Agent (Qwen-VL) initialized successfully.")
        except Exception as e:
            print(f"Failed to load Qwen-VL model: {e}")
            self.model = self.processor = None

    def analyze_image(self, image: Image.Image, prompt: str):
        if not self.model or not self.processor:
            return {"prompt": prompt, "analysis": "Product Research Agent is not initialized."}
        
        print(f"Qwen-VL Agent received prompt: '{prompt}'")
        
        messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": prompt}]}]
        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.processor(text, [image], return_tensors="pt").to(self.device)

        try:
            generated_ids = self.model.generate(**inputs, max_new_tokens=512)
            
            # Remove the input tokens from the generated output
            generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, generated_ids)]
            
            response = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            analysis_text = response.strip()
        except Exception as e:
            print(f"An error occurred during Qwen-VL generation: {e}")
            analysis_text = f"Sorry, an error occurred during image analysis. Error: {e}"

        return {"prompt": prompt, "analysis": analysis_text}

# Singleton instance
product_agent = ProductResearchAgent()