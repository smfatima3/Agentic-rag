# FILE: /kaggle/working/Agentic-rag/scripts/ingest_data.py
# ACTION: Replace the content of your script with this code.
# REASON: This version merges local text data with image data from Hugging Face
#         to create a rich, searchable RAG index.

import os
import json
import pandas as pd
import numpy as np
import faiss
import datasets
import requests
from PIL import Image
from io import BytesIO
from sentence_transformers import SentenceTransformer

def setup_rag_pipeline():
    """
    Builds a RAG pipeline by merging local product descriptions with image data,
    creating image embeddings using the CLIP model, and saving the
    FAISS index and corresponding rich text data.
    """
    print("Starting RAG pipeline setup with LOCAL DATA integration...")

    # --- 1. Define Paths and Load Model ---
    
    # Path to your local data file on Kaggle
    local_data_path = '/kaggle/input/data-for-this-project/shopping_queries_dataset_products.parquet'
    
    # Define the output directory in your writable /kaggle/working space
    # Assuming you run this script from the root of your project `/kaggle/working/Agentic-rag/`
    output_rag_path = 'backend/app/rag_data'

    print("Loading CLIP model: clip-ViT-B-32")
    clip_model = SentenceTransformer('clip-ViT-B-32')

    # --- 2. Load and Prepare Datasets ---

    # Load local product text data
    print(f"Loading local product data from: {local_data_path}")
    if not os.path.exists(local_data_path):
        print(f"FATAL: Local data file not found at {local_data_path}. Aborting.")
        return
    local_products_df = pd.read_parquet(local_data_path)
    print(f"Loaded {len(local_products_df)} records from local parquet file.")

    # Load image URL data from Hugging Face
    print("Loading image URL data from 'crossingminds/shopping-queries-image-dataset'...")
    image_url_ds = datasets.load_dataset("crossingminds/shopping-queries-image-dataset", "product_image_urls", split='train')
    image_url_df = image_url_ds.to_pandas()
    print(f"Loaded {len(image_url_df)} image URL records from Hugging Face.")

    # --- 3. Merge Data Sources ---

    print("Merging local text data with image URL data on 'product_id'...")
    # Perform an 'inner' merge to keep only products that have both text and an image URL
    merged_df = pd.merge(local_products_df, image_url_df, on="product_id", how="inner")
    print(f"Found {len(merged_df)} products with both text descriptions and image URLs.")

    # For demonstration, use a smaller, more manageable subset
    sample_size = 2000
    if len(merged_df) > sample_size:
        merged_df = merged_df.sample(n=sample_size, random_state=42)
    print(f"Using a sample of {len(merged_df)} products for processing.")

    # --- 4. Create Embeddings from Images ---

    print("Generating image embeddings using CLIP...")
    embeddings = []
    valid_products_metadata = [] # This will store the rich metadata for indexed products

    for _, row in merged_df.iterrows():
        image_url = row.get('image_url')
        if not image_url:
            continue
        try:
            # Download the image
            response = requests.get(image_url, timeout=10)
            response.raise_for_status() # Raise an exception for bad status codes
            img = Image.open(BytesIO(response.content)).convert("RGB") # Ensure image is RGB
            
            # Encode the image
            embedding = clip_model.encode([img])[0]
            embeddings.append(embedding)

            # If successful, save the rich metadata including the description
            valid_products_metadata.append({
                "product_id": row.product_id,
                "product_title": row.product_title,
                "product_description": row.product_description,
                "image_url": row.image_url
            })

        except (requests.exceptions.RequestException, IOError, OSError) as e:
            # Skip images that fail to download or process
            continue

    if not embeddings:
        print("FATAL: No images could be processed. Aborting.")
        return

    embeddings_np = np.array(embeddings, dtype='float32')
    print(f"Embeddings created successfully with shape: {embeddings_np.shape}")

    # --- 5. Build and Save FAISS Index and Metadata ---

    dimension = embeddings_np.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_np)

    os.makedirs(output_rag_path, exist_ok=True)

    index_path = os.path.join(output_rag_path, 'product_reviews.index')
    print(f"Saving FAISS index to {index_path}")
    faiss.write_index(index, index_path)

    # Save the corresponding rich product data, which now includes the description
    data_path = os.path.join(output_rag_path, 'product_data.json')
    print(f"Saving rich product data for {len(valid_products_metadata)} valid products to {data_path}")
    
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(valid_products_metadata, f, indent=4)

    print("\n------------------------------------")
    print("RAG pipeline setup complete!")
    print(f"FAISS index and product data saved in: {output_rag_path}")
    print("------------------------------------")

if __name__ == "__main__":
    setup_rag_pipeline()
