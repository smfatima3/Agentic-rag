# FILE: scripts/ingest_data.py
# ACTION: Replace your existing file with this code.
# REASON: This reverts to downloading data directly from Hugging Face,
#         which is more reliable in the Kaggle network environment and
#         solves the "No images could be processed" error.

import datasets
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import os
import json
from PIL import Image
import requests
from io import BytesIO

def setup_rag_pipeline():
    """
    Downloads the dataset from Hugging Face, creates embeddings using the CLIP model,
    and saves the FAISS index and corresponding data.
    """
    print("--- Starting RAG pipeline setup with CLIP model from Hugging Face ---")

    # --- Use the correct CLIP model ---
    print("Loading CLIP model: clip-ViT-B-32")
    model = SentenceTransformer('clip-ViT-B-32')

    # 1. Load the dataset from Hugging Face
    print("Loading dataset: crossingminds/shopping-queries-image-dataset")
    # This dataset contains the image URLs
    try:
        ds = datasets.load_dataset("crossingminds/shopping-queries-image-dataset", "product_image_urls")
        product_data = ds['train']
    except Exception as e:
        print(f"FATAL ERROR: Could not download dataset from Hugging Face: {e}")
        print("Please ensure internet access is enabled in your Kaggle notebook settings.")
        return

    # For demonstration, we'll use a smaller, manageable subset to run quickly.
    sample_size = 5000 # Increased sample size for a richer dataset
    product_data = product_data.select(range(sample_size))
    print(f"Using a sample of {sample_size} products.")

    # 2. Create the embeddings from images
    print("Generating image embeddings using CLIP (this may take a while)...")
    
    embeddings = []
    valid_products = [] # We will only keep products where the image was successfully downloaded

    for item in product_data:
        image_url = item.get('image_url')
        if not image_url:
            continue
        try:
            # Download the image
            response = requests.get(image_url, timeout=10)
            response.raise_for_status() # Raise an exception for bad status codes
            img = Image.open(BytesIO(response.content))
            
            # Encode the image
            embedding = model.encode([img])[0]
            embeddings.append(embedding)
            valid_products.append(item)

        except (requests.exceptions.RequestException, IOError, OSError) as e:
            # Skip images that fail to download or process
            continue

    if not embeddings:
        print("Error: No images could be processed. Aborting.")
        return

    embeddings = np.array(embeddings)
    print(f"Embeddings created successfully with shape: {embeddings.shape}")

    # 3. Build and save the FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings, dtype='float32'))

    rag_data_path = 'backend/app/rag_data'
    os.makedirs(rag_data_path, exist_ok=True)

    index_path = os.path.join(rag_data_path, 'product_reviews.index')
    print(f"Saving FAISS index to {index_path}")
    faiss.write_index(index, index_path)

    # 4. Save the corresponding valid product data
    data_path = os.path.join(rag_data_path, 'product_data.json')
    print(f"Saving metadata for {len(valid_products)} valid products to {data_path}")
    
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(valid_products, f)

    print("--- RAG pipeline setup from Hugging Face complete! ---")

if __name__ == "__main__":
    setup_rag_pipeline()
