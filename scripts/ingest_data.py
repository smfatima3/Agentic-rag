# FILE: scripts/ingest_data.py
# ACTION: Replace your existing file with this code.
# REASON: This adds 'ValueError' to the try...except block, making the script
#         robust by simply skipping any image that causes the channel dimension error.

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

    print("Loading CLIP model: clip-ViT-B-32")
    model = SentenceTransformer('clip-ViT-B-32')

    print("Loading dataset: crossingminds/shopping-queries-image-dataset")
    try:
        ds = datasets.load_dataset("crossingminds/shopping-queries-image-dataset", "product_image_urls")
        product_data = ds['train']
    except Exception as e:
        print(f"FATAL ERROR: Could not download dataset from Hugging Face: {e}")
        return

    sample_size = 5000
    product_data = product_data.select(range(sample_size))
    print(f"Using a sample of {sample_size} products.")

    print("Generating image embeddings using CLIP (this may take a while)...")
    
    embeddings = []
    valid_products = []
    skipped_count = 0

    for item in product_data:
        image_url = item.get('image_url')
        if not image_url:
            continue
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            
            img = img.convert("RGB")
            
            # --- THIS IS THE FIX ---
            # The model.encode() call is now inside the try...except block
            # to catch ValueErrors from problematic images.
            embedding = model.encode([img])[0]
            
            embeddings.append(embedding)
            valid_products.append(item)

        except (requests.exceptions.RequestException, IOError, OSError, ValueError) as e:
            # If any error occurs (download, file format, or value error), skip this image.
            skipped_count += 1
            continue

    if not embeddings:
        print("Error: No images could be processed at all. Aborting.")
        return

    print(f"Total images skipped due to errors: {skipped_count}")
    embeddings = np.array(embeddings)
    print(f"Embeddings created successfully with shape: {embeddings.shape}")

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings, dtype='float32'))

    rag_data_path = 'backend/app/rag_data'
    os.makedirs(rag_data_path, exist_ok=True)

    index_path = os.path.join(rag_data_path, 'product_reviews.index')
    print(f"Saving FAISS index to {index_path}")
    faiss.write_index(index, index_path)

    data_path = os.path.join(rag_data_path, 'product_data.json')
    print(f"Saving metadata for {len(valid_products)} valid products to {data_path}")
    
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(valid_products, f)

    print("--- RAG pipeline setup from Hugging Face complete! ---")

if __name__ == "__main__":
    setup_rag_pipeline()
