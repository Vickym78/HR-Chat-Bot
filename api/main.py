import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from .models import ChatQuery, ChatResponse, Employee
from .rag_system import RAGSystem

app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    print("Application starting up...")
    data_path = Path(__file__).parent.parent / "data" / "employees.json"
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY not found. Please set it in your .env file.")
    app_state["rag_system"] = RAGSystem(data_path=data_path)
    print("RAG System loaded and ready.")
    yield
    app_state.clear()
    print("Application shutting down.")

app = FastAPI(title="HR Chatbot API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.post("/chat", response_model=ChatResponse)
async def chat_with_bot(chat_query: ChatQuery = Body(...)):
    rag_system: RAGSystem = app_state["rag_system"]
    RELEVANCE_THRESHOLD = 1.0
    retrieved_employees, scores = rag_system.search(chat_query.query)
    
    if retrieved_employees and scores[0][0] < RELEVANCE_THRESHOLD:
        print(f"Handling as HR Query. Top score: {scores[0][0]}")
        answer = rag_system.generate_hr_response(chat_query.query, retrieved_employees)
        return ChatResponse(answer=answer, retrieved_employees=retrieved_employees)
    else:
        score_info = scores[0][0] if retrieved_employees else 'N/A'
        print(f"Handling as General Chat. Top score: {score_info}")
        answer = rag_system.generate_general_response(chat_query.query)
        return ChatResponse(answer=answer, retrieved_employees=[])

@app.get("/employees/search", response_model=List[Employee])
async def search_employees(q: str):
    rag_system: RAGSystem = app_state["rag_system"]
    retrieved_employees, _ = rag_system.search(q, top_k=5)
    return retrieved_employees