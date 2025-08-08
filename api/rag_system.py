import json
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
import faiss
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from .models import Employee

class RAGSystem:
    def __init__(self, data_path: Path):
        self.employees = self._load_data(data_path)
        self.employee_map = {emp['id']: emp for emp in self.employees}
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents = self._create_documents()
        print("Creating embeddings and FAISS index...")
        self.index = self._create_faiss_index()
        print("RAG System initialized successfully.")
        self.openai_client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY"),
        )

    def _load_data(self, data_path: Path) -> List[Dict[str, Any]]:
        with open(data_path, 'r') as f:
            data = json.load(f)
        return data['employees']

    def _create_documents(self) -> List[str]:
        docs = []
        for emp in self.employees:
            doc = (f"Name: {emp['name']}. Experience: {emp['experience_years']} years. "
                   f"Skills: {', '.join(emp['skills'])}. Past Projects: {', '.join(emp['projects'])}. "
                   f"Notes: {emp.get('notes', 'N/A')}")
            docs.append(doc)
        return docs

    def _create_faiss_index(self):
        embeddings = self.embedding_model.encode(self.documents, convert_to_tensor=False)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index = faiss.IndexIDMap(index)
        ids = np.array([emp['id'] for emp in self.employees])
        index.add_with_ids(embeddings, ids)
        return index

    def search(self, query: str, top_k: int = 3) -> Tuple[List[Employee], np.ndarray]:
        """
        Performs semantic search and returns employees and their distances (scores).
        A lower distance means a better match.
        """
        query_embedding = self.embedding_model.encode([query])
        distances, ids = self.index.search(query_embedding, top_k)
        retrieved_employees = []
        for i in range(ids.shape[1]):
            employee_id = ids[0, i]
            if employee_id != -1:
                retrieved_employees.append(Employee(**self.employee_map[employee_id]))
        return retrieved_employees, distances

    def generate_hr_response(self, query: str, context_employees: List[Employee]) -> str:
        """Generates a response in the persona of an HR assistant."""
        context_str = "\n---\n".join([json.dumps(emp.model_dump()) for emp in context_employees])
        prompt = f"You are an intelligent HR assistant... Based on the user query '{query}' and these profiles:\n{context_str}\n...generate a helpful recommendation."
        # A more detailed prompt can be used here as before
        
        return self._call_llm(prompt, "You are an intelligent HR assistant chatbot.")

    def generate_general_response(self, query: str) -> str:
        """Generates a response in the persona of a friendly assistant."""
        return self._call_llm(query, "You are a friendly and helpful conversational AI assistant.")

    def _call_llm(self, user_prompt: str, system_prompt: str) -> str:
        """A helper method to call the LLM API."""
        try:
            response = self.openai_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling LLM API: {e}")
            return "I'm sorry, I encountered an error while generating a response. Please try again."