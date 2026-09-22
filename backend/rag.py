
import os
import chromadb

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

DB_PATH = os.getenv(
    "CHROMA_DB_PATH",
    os.path.join(
        os.path.dirname(__file__),
        "chroma_db"
    )
)

chroma_client = chromadb.PersistentClient(
    path=DB_PATH
)

collection = chroma_client.get_or_create_collection(
    name="course_recommendations"
)


def create_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding


def retrieve_courses(query, top_k=10):
    if collection.count() == 0:
        return []

    query_embedding = create_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas"]
    )

    courses = []

    for metadata in results["metadatas"][0]:
        courses.append(metadata)

    return courses