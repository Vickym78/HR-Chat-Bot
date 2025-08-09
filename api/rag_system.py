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
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents = self._create_documents()
        self.index = self._create_faiss_index()
        self.openai_client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY"),
        )

    def _load_data(self, data_path: Path) -> List[Dict[str, Any]]:
        with open(data_path, 'r') as f:
            return json.load(f)['employees']

    def _create_documents(self) -> List[str]:
        docs = []
        for emp in self.employees:
            docs.append(
                f"Name: {emp['name']}. Experience: {emp['experience_years']} years. "
                f"Skills: {', '.join(emp['skills'])}. Past Projects: {', '.join(emp['projects'])}. "
                f"Notes: {emp.get('notes', 'N/A')}"
            )
        return docs

    def _create_faiss_index(self):
        embeddings = self.embedding_model.encode(self.documents, convert_to_tensor=False)
        index = faiss.IndexIDMap(faiss.IndexFlatL2(embeddings.shape[1]))
        ids = np.array([emp['id'] for emp in self.employees])
        index.add_with_ids(embeddings, ids)
        return index

    def search(self, query: str, top_k: int = 3) -> Tuple[List[Employee], np.ndarray]:
        query_embedding = self.embedding_model.encode([query])
        distances, ids = self.index.search(query_embedding, top_k)
        retrieved_employees = [Employee(**self.employee_map[employee_id]) for employee_id in ids[0] if employee_id != -1]
        return retrieved_employees, distances

    def generate_hr_response(self, query: str, context_employees: List[Employee]) -> str:
        context_str = "\n---\n".join([json.dumps(emp.model_dump()) for emp in context_employees])
        user_prompt = f"Based on the user query '{query}' and these profiles:\n{context_str}\n...generate a helpful recommendation."
        system_prompt = (
            "You are an intelligent HR assistant chatbot. Always format your responses using Markdown. "
            "Use lists, bolding, and italics to make the information clear and readable. "
            "For example, recommend candidates using a bulleted list."
        )
        return self._call_llm(user_prompt, system_prompt)

    def generate_general_response(self, query: str) -> str:
        system_prompt = (
            "You are a friendly and helpful conversational AI assistant. "
            "Always use Markdown for all formatting. For code snippets, you MUST use triple backticks "
            "with the language name. For example: ```python\n# Your code here\nprint('Hello')\n```"
        )
        return self._call_llm(query, system_prompt)

    def _call_llm(self, user_prompt: str, system_prompt: str) -> str:
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
            return "I'm sorry, I encountered an error while generating a response."