
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel, Field

from recommender import recommend_courses

load_dotenv()

app = FastAPI(
    title="AI Course Recommendation Chatbot",
    version="1.0.0"
)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Allow React frontend to communicate with FastAPI.
# Restrict this to the deployed frontend URL later.
app.add_middleware(
    CORSMiddleware,
      allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://course-recommendation-chatbot-1.onrender.com/"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"]
)


class RecommendationRequest(BaseModel):
    topic: str = Field(min_length=2)
    budget: str = "any"
    level: str = "any"
    limit: int = Field(default=6, ge=1, le=20)


class ChatRequest(RecommendationRequest):
    history: list[dict[str, str]] = Field(
        default_factory=list
    )


@app.get("/")
def home():
    return {
        "message": "Course Recommendation API is running"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/recommend")
def recommend(request: RecommendationRequest):
    courses = recommend_courses(
        topic=request.topic,
        budget=request.budget,
        level=request.level,
        limit=request.limit
    )

    return {
        "topic": request.topic,
        "total": len(courses),
        "courses": courses
    }


@app.post("/chat")
def chat(request: ChatRequest):
    courses = recommend_courses(
        topic=request.topic,
        budget=request.budget,
        level=request.level,
        limit=request.limit
    )

    if not courses:
        return {
            "response": (
                "I couldn't find matching courses "
                "in the current catalog. Try another "
                "topic or adjust your filters."
            ),
            "courses": []
        }

    course_details = "\n\n".join(
        (
            f"Title: {course['title']}\n"
            f"Provider: {course['provider']}\n"
            f"Level: {course['level']}\n"
            f"Pricing: {course['pricing']}\n"
            f"URL: {course['url']}\n"
            f"Description: {course['description']}"
        )
        for course in courses
    )

    system_prompt = """
You are a professional AI course recommendation assistant.

Recommend courses using ONLY the supplied course catalog.

Rules:
- Never invent courses, prices, certificates or URLs.
- Respect the user's budget and skill-level filters.
- Explain why the courses match the user's goals.
- Distinguish free courses from free-to-audit courses.
- Do not claim prices or certificates are live-verified.
- Keep recommendations concise and well structured.
- Include a simple learning sequence when useful.
"""

    history = [
        {
            "role": message["role"],
            "content": message["content"]
        }
        for message in request.history[-6:]
        if message.get("role") in ["user", "assistant"]
        and isinstance(message.get("content"), str)
    ]

    try:
        response = client.responses.create(
            model="gpt-5-mini",
            instructions=system_prompt,
            input=[
                *history,
                {
                    "role": "user",
                    "content": (
                        f"Learning goal: {request.topic}\n"
                        f"Budget: {request.budget}\n"
                        f"Level: {request.level}\n\n"
                        f"Available courses:\n{course_details}"
                    )
                }
            ]
        )

        return {
            "response": response.output_text,
            "courses": courses
        }

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail="AI recommendation service is unavailable"
        ) from error