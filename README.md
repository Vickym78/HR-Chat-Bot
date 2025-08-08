# HR Resource Query Chatbot 🤖

## Overview
This project is an intelligent HR assistant chatbot designed to help HR teams and project managers find suitable employees using natural language queries. The system leverages a Retrieval-Augmented Generation (RAG) architecture, powered by the free and high-speed **Groq** API, to provide accurate, context-aware, and detailed recommendations.

The application features a sophisticated dual-persona system. It intelligently determines user intent based on query relevance, acting as a professional HR assistant for staffing requests and as a friendly conversationalist for general small talk. The entire experience is wrapped in a polished and interactive user interface built with **Streamlit**.



## Features
- **Natural Language Queries**: Ask complex questions like "Find Python developers with 3+ years of experience" or "Who has worked on healthcare projects?"
- **Dual-Persona Chatbot**: Intelligently switches between a professional HR assistant and a friendly conversationalist based on whether the query is HR-related or general chat.
- **Advanced RAG Pipeline**:
  - **Retrieval**: Uses `sentence-transformers` and `FAISS` for efficient semantic search to find relevant employee profiles.
  - **Relevance-Scoring**: Employs a similarity score threshold to accurately detect user intent without extra API calls.
  - **Generation**: Leverages the high-speed **Groq** API (running Llama 3) to generate insightful, human-like responses.
- **Polished & Interactive UI**: A custom-styled Streamlit interface featuring:
    - A professional sidebar with instructions.
    - Dynamic "streaming" text for bot responses.
    - Visually appealing employee cards with icons, colors, and clickable expanders.
- **Free & Fast**: The entire backend runs on Groq's free tier, providing real-time responses without cost.

## Architecture
The system follows a decoupled architecture, with logic to handle different types of user queries.

1.  **Frontend (UI)**: A **Streamlit** application provides the interactive chat interface.
2.  **Backend (API)**: A **FastAPI** server exposes REST endpoints.
3.  **AI Core (RAG System)**: The backend orchestrates the AI logic:
    - **Search**: A user query is converted into a vector embedding and searched against a pre-indexed `FAISS` database of employee profiles.
    - **Intent Detection**: The system checks the relevance score of the search results.
        - If the score is high (below a set threshold), the query is flagged as **HR-related**.
        - If the score is low, it's flagged as **general chat**.
    - **Generation**:
        - For **HR queries**, the retrieved employee profiles are "augmented" to the prompt sent to the Groq API.
        - For **general chat**, the query is sent directly to the Groq API with a simpler, conversational prompt.

**Flow Diagram:**
`User Query` -> `FastAPI` -> `FAISS Search & Scoring` -> `Intent Check (HR vs. General)` -> `Conditional Prompting` -> `Groq API Call` -> `Formatted Response` -> `Streamlit UI`

## Setup & Installation

**Prerequisites:**
- Python 3.9+
- A free **Groq API Key**

**Instructions:**

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd hr-chatbot
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Get your Groq API Key:**
    - Go to [https://console.groq.com/](https://console.groq.com/), sign up for a free account.
    - Navigate to **API Keys** and create a new key. Copy it.

5.  **Set up your environment variables:**
    - Create a file named `.env` in the root project directory.
    - Add your Groq API key to it:
      ```
      GROQ_API_KEY="gsk_YourCopiedGroqKeyHere"
      ```

6.  **Run the application (in two terminals):**

    - **Terminal 1: Start the Backend API**
      ```bash
      uvicorn api.main:app --reload
      ```
    - **Terminal 2: Start the Frontend UI**
      ```bash
      streamlit run ui/app.py
      ```

## API Documentation
The API is self-documenting. Visit `http://127.0.0.1:8000/docs` while the server is running for a full interactive Swagger UI. The main endpoint is `POST /chat`.

## AI Development Process
This project was developed with significant assistance from AI tools, embodying a modern, iterative development workflow.

-   **AI Coding Assistants Used:** ChatGPT-4 was used for planning, boilerplate generation, and debugging.

-   **How AI Helped in Different Phases:**
    1.  **Initial Planning & Architecture:** The AI helped outline the initial RAG architecture using FastAPI and Streamlit.
    2.  **Problem Solving & Pivoting:** When the initial plan to use the OpenAI API was blocked by quota limits, I used the AI to brainstorm and research free alternatives. It helped identify **Groq** as a suitable replacement due to its speed and OpenAI-compatible API, which minimized the required code changes.
    3.  **Advanced Feature Development:** To handle general conversation, I collaborated with the AI to design the **relevance score threshold** logic. This was a more elegant and efficient solution than adding a separate intent-classification API call.
    4.  **UI/UX Prototyping:** I described the desired "cooler UI" to the AI, which generated the initial custom CSS and the Python code structure for the styled employee cards, streaming text, and sidebar layout.
    5.  **Debugging:** Throughout the process, I pasted tracebacks (like `ImportError`, `NameError`, and `StreamlitInvalidColumnSpecError`) into the AI, which quickly identified the root causes (e.g., incorrect execution, missing imports, or zero-value arguments) and provided the correct fixes.

-   **Code Percentage:**
    -   **AI-Assisted (Generated/Refined): ~50%**. This includes boilerplate, data, CSS, and initial function structures.
    -   **Hand-Written (Authored/Integrated): ~50%**. This includes the final integration of all components, tuning the RAG and UI logic, and writing all documentation.

## Technical Decisions

-   **OpenAI vs. Groq:** The project was initially designed for OpenAI but pivoted to **Groq** due to cost constraints. Groq was the ideal choice because its OpenAI-compatible API allowed for a seamless transition, and its free tier and incredible speed offered a superior developer and user experience for this project's scale.
-   **Intent Detection (Relevance Threshold):** To enable general conversation, I considered using a second LLM call to classify intent. However, I chose the **relevance score threshold** method instead. It reuses the existing vector search results, making it far more efficient (zero extra latency or cost) and demonstrating a more sophisticated use of the RAG pipeline.
-   **UI Framework (Streamlit):** **Streamlit** was chosen for its ability to create beautiful, interactive data apps with pure Python. Its simplicity allowed for rapid prototyping, and its flexibility was demonstrated by the integration of custom CSS to create a polished, non-default look and feel.

## Future Improvements
- **Chat History:** Implement true conversational memory, allowing the chatbot to remember previous turns of the conversation for follow-up questions.
- **Database Integration:** Replace the static `employees.json` file with a proper database (like PostgreSQL with `pgvector`) to allow for dynamic management of the employee roster through a UI.
- **Actionable UI:** Add buttons to the employee cards, such as "Email [Name]" (using a `mailto:` link) or "View Full Resume," to make the application more of a functional tool.

## Demo
*(This is where you would add screenshots of the final, polished application.)*

**The Main Interface:**


**An HR Query Interaction:**