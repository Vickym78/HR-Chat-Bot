# HR Resource Query Chatbot 🤖

## Overview
This project is an intelligent HR assistant chatbot designed to help find suitable employees using natural language queries. The system leverages a Retrieval-Augmented Generation (RAG) architecture, powered by the free and high-speed **Groq** API, to provide accurate, context-aware recommendations.

The application features a sophisticated dual-persona system, intelligently determining user intent to act as a professional HR assistant for staffing requests or as a friendly conversationalist for general small talk. The experience is wrapped in a polished and interactive user interface built with **Streamlit**.

## Features
- **Natural Language Queries**: Ask complex questions like "Find Python developers with 3+ years of experience."
- **Dual-Persona Chatbot**: Intelligently switches between a professional HR assistant and a friendly conversationalist.
- **Advanced RAG Pipeline**: Uses `sentence-transformers` and `FAISS` for efficient semantic search and a relevance score threshold to detect user intent.
- **Polished & Interactive UI**: A custom-styled Streamlit interface with a professional sidebar, dynamic streaming text, and clickable example prompts.
- **Free & Fast**: The entire backend runs on Groq's free tier, providing real-time responses without cost.

## Architecture
`User Query` -> `FastAPI` -> `FAISS Search & Scoring` -> `Intent Check (HR vs. General)` -> `Conditional Prompting` -> `Groq API Call` -> `Formatted Response` -> `Streamlit UI`

## Setup & Installation

**Prerequisites:**
- Python 3.9+
- A free **Groq API Key**

**Instructions:**

1.  **Clone the repository and `cd` into it.**
2.  **Create a virtual environment:** `python -m venv venv` and activate it.
3.  **Install dependencies:** `pip install -r requirements.txt`
4.  **Get your Groq API Key** from [https://console.groq.com/](https://console.groq.com/).
5.  **Create a `.env` file** in the root directory and add your key:
    ```
    GROQ_API_KEY="gsk_YourSecretGroqApiKeyHere"
    ```
6.  **Run the application (in two terminals):**
    - **Terminal 1 (Backend):** `uvicorn api.main:app --reload`
    - **Terminal 2 (Frontend):** `streamlit run ui/app.py`

## Deployment
This application is designed for easy deployment on modern cloud platforms.
1.  **Backend (FastAPI)**: Deploy as a "Web Service" on **Render**. Use `sh run_server.sh` as the start command and securely add `GROQ_API_KEY` as an environment variable.
2.  **Frontend (Streamlit)**: Deploy on **Streamlit Community Cloud**. Update the `API_BASE_URL` in `ui/app.py` to point to your live Render service URL before deploying.