# <<02-JUN-2025:20:02>> - Initial prototype of Screenshot Vectorizer and Analyzer
# Purpose: Vectorize screenshots, store in ChromaDB, and use local LLM for classification

import os
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel
import chromadb
from chromadb.utils import embedding_functions

# Initialize ChromaDB client
chroma_client = chromadb.Client()
collection = chroma_client.create_collection("screenshot_vectors")

# Initialize CLIP model (can sub with BLIP if needed)
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Directory for screenshot ingestion
SCREENSHOT_DIR = "screenshots"


def vectorize_image(image_path):
	image = Image.open(image_path)
	inputs = clip_processor(images=image, return_tensors="pt")
	with torch.no_grad():
		outputs = clip_model.get_image_features(**inputs)
	vector = outputs / outputs.norm(p=2, dim=-1, keepdim=True)
	return vector[0].tolist()


def index_screenshots():
	for root, _, files in os.walk(SCREENSHOT_DIR):
		for file in files:
			if file.endswith(".png"):
				full_path = os.path.join(root, file)
				vector = vectorize_image(full_path)
				doc_id = os.path.splitext(file)[0]
				collection.add(
					documents=[full_path],
					metadatas=[{"file": full_path}],
					ids=[doc_id],
					embeddings=[vector]
				)
	print("✅ Screenshots indexed.")


def find_similar_screens(image_path, n_results=3):
	query_vector = vectorize_image(image_path)
	results = collection.query(query_embeddings=[query_vector], n_results=n_results)
	return results


if __name__ == "__main__":
	index_screenshots()
	# Example usage
	query_image = "screenshots/query.png"
	matches = find_similar_screens(query_image)
	print("Top matches:", matches)
