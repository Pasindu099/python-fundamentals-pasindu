import os
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai
import json


#api key load
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

genai.configure(api_key=api_key)    

print("API Key loaded and Generative AI configured.\n")




# Load article from text file into DataFrame
file_path = 'articles/deep_learning.txt'

with open(file_path, 'r', encoding='utf-8') as file:
    article_content = file.read()

df = pd.DataFrame({
    "article_id": [1],
    "content": [article_content]
})

print("DataFrame loaded successfully!")
print("Number of characters in text:", len(df.loc[0, "content"]))
print("\nFirst 500 characters:\n")
print(df.loc[0, "content"][:500])


#chunking function
def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text (str): The full article text.
        chunk_size (int): Number of characters per chunk.
        overlap (int): Number of characters the next chunk overlaps with the previous one.
        
    Returns:
        List[str]: A list of text chunks.
    """
    
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        
        if end < len(text):
            last_period = chunk.rfind(".")
            if last_period != -1 and last_period > chunk_size // 2:
                end = start + last_period + 1
                chunk = text[start:end]

        chunks.append(chunk.strip())
        start = end - overlap  

    return chunks

# Chunk the article content
article_text = df.loc[0, "content"]
chunks = chunk_text(article_text, chunk_size=1000, overlap=200)

print(f"\nTotal chunks created: {len(chunks)}")
print("\nFirst chunk preview:\n")
print(chunks[0][:500])  


#generating embeddings for chunks
embeddings = []

for i, chunk in enumerate(chunks):
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=chunk
    )   

    embedding = result["embedding"]
    embeddings.append(embedding)

    if i % 5 == 0:
        print(f"Processed chunk {i}/{len(chunks)}")

print("\nEmbedding generation complete!")
print(f"Total embeddings created: {len(embeddings)}")

# Save chunks and embeddings to JSON file
output_path = "chunk_embeddings.json"

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(embeddings, f, ensure_ascii=False, indent=2)

print(f"\nAll embeddings saved successfully to: {output_path}")
