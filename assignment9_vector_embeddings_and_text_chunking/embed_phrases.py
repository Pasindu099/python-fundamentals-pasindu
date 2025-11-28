import os
from dotenv import load_dotenv
import google.generativeai as genai
from sklearn.metrics.pairwise import cosine_similarity


load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY") 
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")
genai.configure(api_key=api_key)    

models = genai.list_models()
for model in models:
   if 'embedding' in model.name:
       print(f"Model Name: {model.name}, Description: {model.description}")

sentences = ["Python for data engineering module is so structured.",
             "I realized it lately.",
             "Now I regret for not actively participating."]

model = genai.GenerativeModel("models/text-embedding-004")

for sentence in sentences:
    print("\nSentence:", sentence)

    result = genai.embed_content(
        model="models/text-embedding-004",
        content=sentence
    )

    embedding = result["embedding"]


    print("Embedding length:", len(embedding))
    print("First 5 values of embedding:", embedding[:5])


embeddings = []
for sentence in sentences:
    print("\nSentence:", sentence)

    result = genai.embed_content(
        model="models/text-embedding-004",
        content=sentence
    )   

    embedding = result["embedding"]

    print("Embedding length:", len(embedding))
    print("First 5 values of embedding:", embedding[:5])

    embeddings.append(embedding)

print("\nCosine Similarity between sentences:")

sim_0_1 = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
sim_0_2 = cosine_similarity([embeddings[0]], [embeddings[2]])[0][0]
sim_1_2 = cosine_similarity([embeddings[1]], [embeddings[2]])[0][0] 

print(f"Sentence 0 and Sentence 1: {sim_0_1}")
print(f"Sentence 0 and Sentence 2: {sim_0_2}")
print(f"Sentence 1 and Sentence 2: {sim_1_2}")

