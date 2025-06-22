# FILE: backend/app/agents/review_analyzer_agent.py
# ACTION: Replace the content of this file with the code below.
# REASON: Fixes a TypeError by converting the numpy.float32 relevance score
#         to a standard Python float, which FastAPI can correctly serialize to JSON.

import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import json
import os

class ReviewAnalyzerAgent:
    def __init__(self):
        """
        Initializes the agent by loading the FAISS index, product data,
        and the sentence transformer model.
        """
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

        except FileNotFoundError as e:
            print(f"ERROR: A required data file was not found: {e}")
            print("Please ensure you have run the 'ingest_data.py' script successfully.")
            self.index = None
            self.product_data = None
            self.model = None
        except Exception as e:
            print(f"An unexpected error occurred during agent initialization: {e}")
            self.index = None
            self.product_data = None
            self.model = None


    def analyze(self, query: str, top_k: int = 5):
        """
        Analyzes a user query to find relevant products and summarize their "reviews".
        """
        if not self.index or not self.product_data or not self.model:
            return {
                "summary": "Sorry, the Review Analyzer Agent is not properly initialized. Please check the server logs for errors.",
                "top_products": []
            }

        print(f"Agent received query: '{query}'")
        # For CLIP, we can search by encoding text or an image. Here we use text.
        query_embedding = self.model.encode([query])

        distances, indices = self.index.search(np.array(query_embedding, dtype='float32'), top_k)

        results = []
        if indices.size == 0:
            return {
                "summary": f"I couldn't find any products matching your query '{query}'. Please try a different search.",
                "top_products": []
            }

        for i in range(top_k):
            idx = indices[0][i]
            product = self.product_data[idx]
            results.append({
                "product_id": product.get("product_id", "N/A"),
                "product_title": product.get("product_title", "No Title"),
                "review_snippet": product.get("product_description", "No Description"),
                "image_url": product.get("image_url", ""),
                
                # --- THIS IS THE FIX ---
                # Convert the numpy.float32 to a standard Python float
                "relevance_score": float(1 - distances[0][i])
            })

        summary = f"Based on your query '{query}', I found several relevant products. For example, '{results[0]['product_title']}' seems like a good match. You can see it at this URL: {results[0]['image_url']}"

        return {
            "summary": summary,
            "top_products": results
        }

# Singleton instance of the agent
review_agent = ReviewAnalyzerAgent()
# This ensures that the agent is initialized only once and can be reused across requests.

