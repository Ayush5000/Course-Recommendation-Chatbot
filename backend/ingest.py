
import os
import json

from rag import collection, create_embedding

BASE_DIR = os.path.dirname(__file__)

DATA_PATH = os.getenv(
    "DATA_PATH",
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../data/courses.json"
        )
    )
)


def ingest_courses():
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        courses = json.load(file)

    for course in courses:
        text = (
            f"Course: {course['title']}. "
            f"Category: {course['category']}. "
            f"Level: {course['level']}. "
            f"Provider: {course['provider']}. "
            f"Description: {course['description']}"
        )

        embedding = create_embedding(text)

        metadata = {
            "title": course["title"],
            "provider": course["provider"],
            "category": course["category"],
            "level": course["level"],
            "pricing": course["pricing"],
            "url": course["url"],
            "description": course["description"],
            "certificate": str(course["certificate"])
        }

        collection.upsert(
            ids=[course["id"]],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata]
        )

        print(f"Stored: {course['title']}")

    print(f"Total courses stored: {collection.count()}")


if __name__ == "__main__":
    ingest_courses()