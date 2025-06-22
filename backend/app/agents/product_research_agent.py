from transformers import AutoProcessor, AutoModelForCausalLM
from PIL import Image
import torch
import os

class ProductResearchAgent:
    def __init__(self):
        """
        Initializes the Product Research Agent by loading the Cohere Aya Vision model.
        This uses 4-bit quantization to reduce memory usage.
        Requires a GPU and a Hugging Face token.
        """
        print("Initializing Product Research Agent with Cohere Aya Vision...")
        
        # Ensure HF_TOKEN is set
        if 'HF_TOKEN' not in os.environ:
            print("WARNING: Hugging Face token (HF_TOKEN) not found in environment variables.")
            # Handle error appropriately in a real app
            self.model = None
            self.processor = None
            return

        self.model_id = "CohereForAI/aya-23-8B"
        
        # Check for GPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        if self.device == "cpu":
            print("WARNING: Running Aya Vision on CPU will be extremely slow. A GPU is highly recommended.")

        try:
            # Load model with 4-bit quantization to save memory
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                torch_dtype=torch.bfloat16,
                device_map=self.device,
                load_in_4bit=True,
                trust_remote_code=True
            )
            self.processor = AutoProcessor.from_pretrained(self.model_id, trust_remote_code=True)
            print("Product Research Agent initialized successfully.")

        except Exception as e:
            print(f"Failed to load Aya Vision model: {e}")
            self.model = None
            self.processor = None

    def analyze_image(self, image: Image.Image, prompt: str):
        """
        Analyzes an image using the Aya Vision model.

        Args:
            image: A PIL Image object.
            prompt: The text prompt/question about the image.

        Returns:
            A dictionary containing the analysis result.
        """
        if not self.model or not self.processor:
            return {
                "prompt": prompt,
                "analysis": "Sorry, the Product Research Agent is not initialized. Please check the server logs."
            }
            
        print(f"Agent received prompt: '{prompt}' for image analysis.")

        # Format the prompt for the model
        # The model expects a specific format for conversation turns.
        messages = [{"role": "user", "content": f"<image>\n{prompt}"}]
        
        # Preprocess the prompt and image
        inputs = self.processor(
            text=self.processor.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            ),
            images=image,
            return_tensors="pt"
        ).to(self.device)

        # Generate a response
        try:
            generation_args = {
                "max_new_tokens": 500,
                "temperature": 0.1,
                "do_sample": True,
            }
            
            generated_ids = self.model.generate(**inputs, **generation_args)
            
            # Decode the response, skipping special tokens
            generated_texts = self.processor.batch_decode(generated_ids, skip_special_tokens=True)
            
            # The output contains the original prompt, so we need to clean it
            # The response is typically after '[/INST]'. We find it and get the text after it.
            raw_text = generated_texts[0]
            inst_token = '[/INST]'
            response_start_index = raw_text.rfind(inst_token)
            if response_start_index != -1:
                analysis_text = raw_text[response_start_index + len(inst_token):].strip()
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
