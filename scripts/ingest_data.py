# FILE: scripts/ingest_data.py
# ACTION: Replace your existing file with this code.
# REASON: This version reads data from your local Parquet file instead of
#         downloading it from Hugging Face, making it much faster and more reliable.

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import os
import json
from PIL import Image
import requests
from io import BytesIO
import pandas as pd # Import pandas

def setup_rag_pipeline():
    """
    Reads the local Parquet file, creates embeddings using the CLIP model,
    and saves the FAISS index and corresponding data.
    """
    print("--- Starting RAG pipeline setup from local Parquet file ---")

    # --- Use the correct CLIP model ---
    print("Loading CLIP model: clip-ViT-B-32")
    model = SentenceTransformer('clip-ViT-B-32')

    # 1. Load the dataset from the local Parquet file
    parquet_path = "/kaggle/input/data-for-this-project/shopping_queries_dataset_products.parquet"
    print(f"Loading dataset from: {parquet_path}")
    
    if not os.path.exists(parquet_path):
        print(f"FATAL ERROR: The specified Parquet file was not found at {parquet_path}")
        print("Please ensure your Kaggle notebook has this dataset added as an input.")
        return # Exit the script if the data is not found

    df = pd.read_parquet(parquet_path)
    
    # Convert dataframe to a list of dictionaries, which is easier to work with
    product_data = df.to_dict('records')
    print(f"Loaded {len(product_data)} products from the Parquet file.")

    # For demonstration, you can still use a subset if the file is very large
    # sample_size = 5000
    # product_data = product_data[:sample_size]
    # print(f"Using a sample of {len(product_data)} products.")

    # 2. Create the embeddings from images
    print("Generating image embeddings using CLIP (this may take a while)...")
    
    embeddings = []
    valid_products = [] # We will only keep products where the image could be processed

    for item in product_data:
        # Assuming the column name for the image URL is 'image_url'
        image_url = item.get('image_url')
        if not image_url:
            continue
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            
            embedding = model.encode([img])[0]
            embeddings.append(embedding)
            valid_products.append(item)

        except Exception as e:
            # Skip images that fail to download or process
            continue

    if not embeddings:
        print("Error: No images could be processed. Please check image URLs and network access. Aborting.")
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

    print("--- RAG pipeline setup from local file complete! ---")

if __name__ == "__main__":
    setup_rag_pipeline()
