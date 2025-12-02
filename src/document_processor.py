from typing import List, Optional
from pydantic import BaseModel
import json
from pathlib import Path


# Pydantic models
class Metadata(BaseModel):
    likes_trading: Optional[bool] = None
    experience_years: Optional[int] = None
    prefers_remote_work: Optional[bool] = None
    gym_member: Optional[bool] = None


class Address(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None


class Document(BaseModel):
    id: int
    name: str
    age: int
    city: str
    email: str

    skills: Optional[List[str]] = None
    hobbies: Optional[List[str]] = None
    active: Optional[bool] = None

    address: Optional[Address] = None
    metadata: Optional[Metadata] = None


# Function to load and validate documents
def load_documents(file_path: str) -> List[Document]:
    """Load JSON file and return validated Document objects."""
    path = Path(file_path)

    with path.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)

    documents: List[Document] = []
    for item in raw_data:
        try:
            documents.append(Document(**item))
        except Exception as e:
            print(f"Skipping invalid document: {item} -> {e}")

    return documents


# Function to display documents
def display_documents(documents: List[Document]) -> None:
    """Print personal-style documents gracefully."""
    for doc in documents:
        print(f"ID: {doc.id} | Name: {doc.name} | Age: {doc.age}")
        print(f"City: {doc.city} | Email: {doc.email}")

        print(f"Skills: {doc.skills if doc.skills else 'None'}")
        print(f"Hobbies: {doc.hobbies if doc.hobbies else 'None'}")
        print(f"Active: {doc.active if doc.active is not None else 'Unknown'}")

        if doc.address:
            print(f"Address: {doc.address.model_dump()}")
        else:
            print("Address: Not available")

        if doc.metadata:
            print(f"Metadata: {doc.metadata.model_dump()}")
        else:
            print("Metadata: Not available")

        print("-" * 40)


# Run manually
if __name__ == "__main__":
    file_path = "data/documents.json"
    documents = load_documents(file_path)
    display_documents(documents)
