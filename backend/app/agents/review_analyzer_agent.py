# FILE: backend/app/agents/review_analyzer_agent.py
# ACTION: Replace your existing file with this complete code.
# REASON: This fixes the 'AttributeError' by including the missing
#         'analyze_with_image' method and improves error handling.

import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import json
import os
from PIL import Image

class ReviewAnalyzerAgent:
    def __init__(self):
        print("Initializing Review Analyzer Agent...")
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.rag_data_path = os.path.join(current_dir, '..', 'rag_data')
            self.index_path = os.path.join(self.rag_data_path, 'product_reviews.index')
            self.data_path = os.path.join(self.rag_data_path, 'product_data.json')

            print("Loading CLIP model for semantic search...")
            self.model = SentenceTransformer('clip-ViT-B-32')

            print(f"Loading FAISS index from {self.index_path}")
            self.index = faiss.read_index(self.index_path)

            print(f"Loading product data from {self.data_path}")
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.product_data = json.load(f)

            print("Review Analyzer Agent initialized successfully.")
        except Exception as e:
            print(f"ERROR during Review Analyzer Agent initialization: {e}")
            print("This might be because the 'ingest_data.py' script has not been run yet.")
            self.index = self.product_data = self.model = None

    def _perform_search(self, query_embedding: np.ndarray, top_k: int):
        """Helper function to perform search and format results."""
        if not self.index or not self.product_data:
            return {"summary": "Agent not initialized.", "top_products": []}

        distances, indices = self.index.search(np.array(query_embedding, dtype='float32'), top_k)
        
        results = []
        if indices.size == 0 or len(indices[0]) == 0:
            return {"summary": "Couldn't find any matching products.", "top_products": []}

        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx < len(self.product_data):
                product = self.product_data[idx]
                results.append({
                    "product_id": product.get("product_id", "N/A"),
                    "product_title": product.get("product_title", "No Title"),
                    "review_snippet": product.get("product_description", "No Description"),
                    "image_url": product.get("image_url", ""),
                    "relevance_score": float(1 - distances[0][i])
                })
        
        if not results:
            return {"summary": "Couldn't find any matching products.", "top_products": []}

        summary = f"Found several similar products. The top match is '{results[0]['product_title']}'."
        return {"summary": summary, "top_products": results}

    def analyze(self, query: str, top_k: int = 5):
        """Analyzes a text query to find relevant products."""
        print(f"Agent received text query: '{query}'")
        if not self.model: return {"summary": "Agent not initialized.", "top_products": []}
        
        query_embedding = self.model.encode([query])
        return self._perform_search(query_embedding, top_k)

    def analyze_with_image(self, image: Image.Image, top_k: int = 5):
        """Analyzes an image to find visually similar products."""
        print("Agent received image for similarity search.")
        if not self.model: return {"summary": "Agent not initialized.", "top_products": []}

        image_embedding = self.model.encode([image])
        return self._perform_search(image_embedding, top_k)

# Singleton instance of the agent
review_agent = ReviewAnalyzerAgent()
