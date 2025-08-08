import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from .models import ChatQuery, ChatResponse, Employee
from .rag_system import RAGSystem

# --- App State ---
app_state = {}

# --- Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    print("Application starting up...")
    data_path = Path(__file__).parent.parent / "data" / "employees.json"
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise ValueError("GROQ_API_KEY not found. Please set it in your .env file.")
    app_state["rag_system"] = RAGSystem(data_path=data_path)
    print("RAG System loaded and ready.")
    yield
    print("Application shutting down...")
    app_state.clear()

# --- FastAPI App Initialization ---
app = FastAPI(
    title="HR Resource Query Chatbot API",
    description="API for the HR chatbot with RAG capabilities",
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# --- API Endpoints ---
@app.post("/chat", response_model=ChatResponse)
async def chat_with_bot(chat_query: ChatQuery = Body(...)):
    """
    Receives a user query and decides whether to handle it as an HR query or general chat.
    """
    rag_system: RAGSystem = app_state.get("rag_system")
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system is not available.")
    
    # This threshold determines how relevant a query must be to be considered an HR query.
    # Lower distance = more relevant. We can tune this value.
    RELEVANCE_THRESHOLD = 1.0

    # 1. Retrieval: Search for employees and get their relevance scores (distances)
    retrieved_employees, scores = rag_system.search(chat_query.query)
    
    # 2. Intent Detection: Check if the top result's score is below the threshold
    is_hr_query = bool(retrieved_employees and scores[0][0] < RELEVANCE_THRESHOLD)
    
    answer = ""
    employees_to_return = []
    
    if is_hr_query:
        # 3a. It's an HR query. Generate a response using the retrieved context.
        print(f"Handling as HR Query. Top score: {scores[0][0]}")
        answer = rag_system.generate_hr_response(chat_query.query, retrieved_employees)
        employees_to_return = retrieved_employees
    else:
        # 3b. It's general chat. Generate a direct, conversational response.
        print(f"Handling as General Chat. Top score: {scores[0][0]}")
        answer = rag_system.generate_general_response(chat_query.query)
        # We don't return any employees for general chat
        employees_to_return = []

    return ChatResponse(answer=answer, retrieved_employees=employees_to_return)

@app.get("/employees/search", response_model=List[Employee])
async def search_employees(q: str):
    rag_system: RAGSystem = app_state.get("rag_system")
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system is not available.")
    retrieved_employees, _ = rag_system.search(q, top_k=5)
    return retrieved_employees